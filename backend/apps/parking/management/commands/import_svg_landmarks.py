"""
从 SVG 地图导入导航地标到 ParkingSpace 表。

用法:
    python manage.py import_svg_landmarks
    python manage.py import_svg_landmarks --svg-path backend/svg/interactive_map.svg --floor B2 --replace
"""

from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from parking.models import ParkingSpace


TRANSFORM_PATTERN = re.compile(r'(translate|matrix)\(([^)]+)\)')


def _parse_numbers(value: str) -> list[float]:
    return [float(part) for part in re.split(r'[\s,]+', value.strip()) if part]


def _identity_matrix() -> tuple[float, float, float, float, float, float]:
    return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _multiply_matrices(
    left: tuple[float, float, float, float, float, float],
    right: tuple[float, float, float, float, float, float],
) -> tuple[float, float, float, float, float, float]:
    left_a, left_b, left_c, left_d, left_e, left_f = left
    right_a, right_b, right_c, right_d, right_e, right_f = right
    return (
        left_a * right_a + left_c * right_b,
        left_b * right_a + left_d * right_b,
        left_a * right_c + left_c * right_d,
        left_b * right_c + left_d * right_d,
        left_a * right_e + left_c * right_f + left_e,
        left_b * right_e + left_d * right_f + left_f,
    )


def _parse_transform(transform_value: str | None) -> tuple[float, float, float, float, float, float]:
    matrix = _identity_matrix()
    if not transform_value:
        return matrix

    for name, raw_args in TRANSFORM_PATTERN.findall(transform_value):
        arguments = _parse_numbers(raw_args)
        if name == 'translate':
            tx = arguments[0] if arguments else 0.0
            ty = arguments[1] if len(arguments) > 1 else 0.0
            local = (1.0, 0.0, 0.0, 1.0, tx, ty)
        elif name == 'matrix' and len(arguments) == 6:
            local = tuple(arguments)  # type: ignore[assignment]
        else:
            continue
        matrix = _multiply_matrices(matrix, local)
    return matrix


def _apply_matrix(
    matrix: tuple[float, float, float, float, float, float],
    x: float,
    y: float,
) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    return (a * x + c * y + e, b * x + d * y + f)


def _extract_label_points(
    element: ET.Element,
    inherited_matrix: tuple[float, float, float, float, float, float],
) -> list[dict[str, object]]:
    current_matrix = _multiply_matrices(inherited_matrix, _parse_transform(element.get('transform')))
    results: list[dict[str, object]] = []

    tag_name = element.tag.split('}', 1)[-1]
    if tag_name == 'text':
        text_content = ''.join(element.itertext()).strip()
        if text_content:
            text_x = 0.0
            text_y = 0.0
            first_tspan = next((child for child in element.iter() if child.tag.split('}', 1)[-1] == 'tspan'), None)
            if first_tspan is not None:
                try:
                    text_x = float(first_tspan.get('x', '0') or 0)
                    text_y = float(first_tspan.get('y', '0') or 0)
                except ValueError:
                    text_x = 0.0
                    text_y = 0.0
            location_x, location_y = _apply_matrix(current_matrix, text_x, text_y)
            results.append({
                'name': text_content,
                'x': location_x,
                'y': location_y,
                'raw_x': current_matrix[4],
                'raw_y': current_matrix[5],
            })

    for child in element:
        results.extend(_extract_label_points(child, current_matrix))

    return results


class Command(BaseCommand):
    help = 'Import SVG landmark nodes into ParkingSpace records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--svg-path',
            type=str,
            default=str(Path(__file__).resolve().parents[4] / 'svg' / 'interactive_map.svg'),
            help='SVG file path to parse',
        )
        parser.add_argument(
            '--floor',
            type=str,
            default=ParkingSpace.Floor.B2,
            choices=[choice for choice, _ in ParkingSpace.Floor.choices],
            help='Floor code to assign to imported landmarks',
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Remove existing location nodes on the same floor before import',
        )

    def handle(self, *args, **options):
        svg_path = Path(options['svg_path'])
        floor = options['floor']
        replace = options['replace']

        if not svg_path.exists():
            raise CommandError(f'SVG file does not exist: {svg_path}')

        try:
            root = ET.parse(svg_path).getroot()
        except ET.ParseError as exc:
            raise CommandError(f'Failed to parse SVG: {exc}') from exc

        if replace:
            removed_count, _ = ParkingSpace.objects.filter(
                floor=floor,
                node_type=ParkingSpace.NodeType.LOCATION,
            ).delete()
            self.stdout.write(self.style.WARNING(f'已清理 {removed_count} 条旧地点节点'))

        labels = _extract_label_points(root, _identity_matrix())
        if not labels:
            self.stdout.write(self.style.WARNING('未在 SVG 中找到可导入的地标文本'))
            return

        created_count = 0
        updated_count = 0

        for index, label in enumerate(labels, start=1):
            location_name = str(label['name'])
            x = float(label['x'])
            y = float(label['y'])
            hash_source = f'{location_name}:{x:.3f}:{y:.3f}'.encode('utf-8')
            space_id = f'loc_{hashlib.md5(hash_source).hexdigest()[:12]}'

            obj, created = ParkingSpace.objects.update_or_create(
                floor=floor,
                node_type=ParkingSpace.NodeType.LOCATION,
                location_name=location_name,
                defaults={
                    'space_id': space_id,
                    'status': False,
                    'type': False,
                    'reserved_plate': None,
                    'current_plate': None,
                    'center_x': x,
                    'center_y': y,
                    'x': x,
                    'y': y,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'[{index}] {obj.location_name} -> space_id={obj.space_id}, x={obj.x:.2f}, y={obj.y:.2f}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'导入完成: 创建={created_count}, 更新={updated_count}, 总数={len(labels)}'
            )
        )