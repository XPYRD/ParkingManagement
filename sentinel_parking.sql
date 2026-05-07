/*
 Navicat Premium Dump SQL

 Source Server         : 阿里云ECS
 Source Server Type    : MySQL
 Source Server Version : 80040 (8.0.40)
 Source Host           : localhost:3306
 Source Schema         : sentinel_parking

 Target Server Type    : MySQL
 Target Server Version : 80040 (8.0.40)
 File Encoding         : 65001

 Date: 07/05/2026 18:33:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_group
-- ----------------------------

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_group_permissions_group_id_permission_id_0cd325b0_uniq`(`group_id` ASC, `permission_id` ASC) USING BTREE,
  INDEX `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_permission_content_type_id_codename_01ab375a_uniq`(`content_type_id` ASC, `codename` ASC) USING BTREE,
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 93 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO `auth_permission` VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO `auth_permission` VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO `auth_permission` VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO `auth_permission` VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO `auth_permission` VALUES (5, 'Can add permission', 3, 'add_permission');
INSERT INTO `auth_permission` VALUES (6, 'Can change permission', 3, 'change_permission');
INSERT INTO `auth_permission` VALUES (7, 'Can delete permission', 3, 'delete_permission');
INSERT INTO `auth_permission` VALUES (8, 'Can view permission', 3, 'view_permission');
INSERT INTO `auth_permission` VALUES (9, 'Can add group', 2, 'add_group');
INSERT INTO `auth_permission` VALUES (10, 'Can change group', 2, 'change_group');
INSERT INTO `auth_permission` VALUES (11, 'Can delete group', 2, 'delete_group');
INSERT INTO `auth_permission` VALUES (12, 'Can view group', 2, 'view_group');
INSERT INTO `auth_permission` VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO `auth_permission` VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO `auth_permission` VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO `auth_permission` VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO `auth_permission` VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO `auth_permission` VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO `auth_permission` VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO `auth_permission` VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO `auth_permission` VALUES (21, 'Can add 用户', 6, 'add_user');
INSERT INTO `auth_permission` VALUES (22, 'Can change 用户', 6, 'change_user');
INSERT INTO `auth_permission` VALUES (23, 'Can delete 用户', 6, 'delete_user');
INSERT INTO `auth_permission` VALUES (24, 'Can view 用户', 6, 'view_user');
INSERT INTO `auth_permission` VALUES (25, 'Can add 车辆', 7, 'add_vehicle');
INSERT INTO `auth_permission` VALUES (26, 'Can change 车辆', 7, 'change_vehicle');
INSERT INTO `auth_permission` VALUES (27, 'Can delete 车辆', 7, 'delete_vehicle');
INSERT INTO `auth_permission` VALUES (28, 'Can view 车辆', 7, 'view_vehicle');
INSERT INTO `auth_permission` VALUES (29, 'Can add 停车位', 9, 'add_parkingspot');
INSERT INTO `auth_permission` VALUES (30, 'Can change 停车位', 9, 'change_parkingspot');
INSERT INTO `auth_permission` VALUES (31, 'Can delete 停车位', 9, 'delete_parkingspot');
INSERT INTO `auth_permission` VALUES (32, 'Can view 停车位', 9, 'view_parkingspot');
INSERT INTO `auth_permission` VALUES (33, 'Can add 停车会话', 8, 'add_parkingsession');
INSERT INTO `auth_permission` VALUES (34, 'Can change 停车会话', 8, 'change_parkingsession');
INSERT INTO `auth_permission` VALUES (35, 'Can delete 停车会话', 8, 'delete_parkingsession');
INSERT INTO `auth_permission` VALUES (36, 'Can view 停车会话', 8, 'view_parkingsession');
INSERT INTO `auth_permission` VALUES (37, 'Can add 车位预约', 10, 'add_reservation');
INSERT INTO `auth_permission` VALUES (38, 'Can change 车位预约', 10, 'change_reservation');
INSERT INTO `auth_permission` VALUES (39, 'Can delete 车位预约', 10, 'delete_reservation');
INSERT INTO `auth_permission` VALUES (40, 'Can view 车位预约', 10, 'view_reservation');
INSERT INTO `auth_permission` VALUES (41, 'Can add 定价规则', 12, 'add_pricingrule');
INSERT INTO `auth_permission` VALUES (42, 'Can change 定价规则', 12, 'change_pricingrule');
INSERT INTO `auth_permission` VALUES (43, 'Can delete 定价规则', 12, 'delete_pricingrule');
INSERT INTO `auth_permission` VALUES (44, 'Can view 定价规则', 12, 'view_pricingrule');
INSERT INTO `auth_permission` VALUES (45, 'Can add 支付记录', 11, 'add_payment');
INSERT INTO `auth_permission` VALUES (46, 'Can change 支付记录', 11, 'change_payment');
INSERT INTO `auth_permission` VALUES (47, 'Can delete 支付记录', 11, 'delete_payment');
INSERT INTO `auth_permission` VALUES (48, 'Can view 支付记录', 11, 'view_payment');
INSERT INTO `auth_permission` VALUES (49, 'Can add 订阅计划', 13, 'add_subscription');
INSERT INTO `auth_permission` VALUES (50, 'Can change 订阅计划', 13, 'change_subscription');
INSERT INTO `auth_permission` VALUES (51, 'Can delete 订阅计划', 13, 'delete_subscription');
INSERT INTO `auth_permission` VALUES (52, 'Can view 订阅计划', 13, 'view_subscription');
INSERT INTO `auth_permission` VALUES (53, 'Can add 设备', 14, 'add_device');
INSERT INTO `auth_permission` VALUES (54, 'Can change 设备', 14, 'change_device');
INSERT INTO `auth_permission` VALUES (55, 'Can delete 设备', 14, 'delete_device');
INSERT INTO `auth_permission` VALUES (56, 'Can view 设备', 14, 'view_device');
INSERT INTO `auth_permission` VALUES (57, 'Can add 系统预警', 15, 'add_alert');
INSERT INTO `auth_permission` VALUES (58, 'Can change 系统预警', 15, 'change_alert');
INSERT INTO `auth_permission` VALUES (59, 'Can delete 系统预警', 15, 'delete_alert');
INSERT INTO `auth_permission` VALUES (60, 'Can view 系统预警', 15, 'view_alert');
INSERT INTO `auth_permission` VALUES (61, 'Can add 用户工单', 16, 'add_ticket');
INSERT INTO `auth_permission` VALUES (62, 'Can change 用户工单', 16, 'change_ticket');
INSERT INTO `auth_permission` VALUES (63, 'Can delete 用户工单', 16, 'delete_ticket');
INSERT INTO `auth_permission` VALUES (64, 'Can view 用户工单', 16, 'view_ticket');
INSERT INTO `auth_permission` VALUES (65, 'Can add AI 识别记录', 17, 'add_recognitionrecord');
INSERT INTO `auth_permission` VALUES (66, 'Can change AI 识别记录', 17, 'change_recognitionrecord');
INSERT INTO `auth_permission` VALUES (67, 'Can delete AI 识别记录', 17, 'delete_recognitionrecord');
INSERT INTO `auth_permission` VALUES (68, 'Can view AI 识别记录', 17, 'view_recognitionrecord');
INSERT INTO `auth_permission` VALUES (69, 'Can add 停车位连接', 18, 'add_spotconnection');
INSERT INTO `auth_permission` VALUES (70, 'Can change 停车位连接', 18, 'change_spotconnection');
INSERT INTO `auth_permission` VALUES (71, 'Can delete 停车位连接', 18, 'delete_spotconnection');
INSERT INTO `auth_permission` VALUES (72, 'Can view 停车位连接', 18, 'view_spotconnection');
INSERT INTO `auth_permission` VALUES (73, 'Can add 车位信息(地图渲染)', 19, 'add_parkingspace');
INSERT INTO `auth_permission` VALUES (74, 'Can change 车位信息(地图渲染)', 19, 'change_parkingspace');
INSERT INTO `auth_permission` VALUES (75, 'Can delete 车位信息(地图渲染)', 19, 'delete_parkingspace');
INSERT INTO `auth_permission` VALUES (76, 'Can view 车位信息(地图渲染)', 19, 'view_parkingspace');
INSERT INTO `auth_permission` VALUES (77, 'Can add 用户余额', 21, 'add_userbalance');
INSERT INTO `auth_permission` VALUES (78, 'Can change 用户余额', 21, 'change_userbalance');
INSERT INTO `auth_permission` VALUES (79, 'Can delete 用户余额', 21, 'delete_userbalance');
INSERT INTO `auth_permission` VALUES (80, 'Can view 用户余额', 21, 'view_userbalance');
INSERT INTO `auth_permission` VALUES (81, 'Can add 充值记录', 20, 'add_topuprecord');
INSERT INTO `auth_permission` VALUES (82, 'Can change 充值记录', 20, 'change_topuprecord');
INSERT INTO `auth_permission` VALUES (83, 'Can delete 充值记录', 20, 'delete_topuprecord');
INSERT INTO `auth_permission` VALUES (84, 'Can view 充值记录', 20, 'view_topuprecord');
INSERT INTO `auth_permission` VALUES (85, 'Can add 订阅套餐', 22, 'add_subscriptionplan');
INSERT INTO `auth_permission` VALUES (86, 'Can change 订阅套餐', 22, 'change_subscriptionplan');
INSERT INTO `auth_permission` VALUES (87, 'Can delete 订阅套餐', 22, 'delete_subscriptionplan');
INSERT INTO `auth_permission` VALUES (88, 'Can view 订阅套餐', 22, 'view_subscriptionplan');
INSERT INTO `auth_permission` VALUES (89, 'Can add 银行卡', 23, 'add_bankcard');
INSERT INTO `auth_permission` VALUES (90, 'Can change 银行卡', 23, 'change_bankcard');
INSERT INTO `auth_permission` VALUES (91, 'Can delete 银行卡', 23, 'delete_bankcard');
INSERT INTO `auth_permission` VALUES (92, 'Can view 银行卡', 23, 'view_bankcard');

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `object_repr` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `content_type_id` int NULL DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `django_admin_log_content_type_id_c4bce8eb_fk_django_co`(`content_type_id` ASC) USING BTREE,
  INDEX `django_admin_log_user_id_c564eba6_fk_sentinel_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `django_admin_log_chk_1` CHECK (`action_flag` >= 0)
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `django_content_type_app_label_model_76bd3d3b_uniq`(`app_label` ASC, `model` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 24 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO `django_content_type` VALUES (6, 'accounts', 'user');
INSERT INTO `django_content_type` VALUES (7, 'accounts', 'vehicle');
INSERT INTO `django_content_type` VALUES (1, 'admin', 'logentry');
INSERT INTO `django_content_type` VALUES (17, 'ai_recognition', 'recognitionrecord');
INSERT INTO `django_content_type` VALUES (15, 'alerts', 'alert');
INSERT INTO `django_content_type` VALUES (16, 'alerts', 'ticket');
INSERT INTO `django_content_type` VALUES (2, 'auth', 'group');
INSERT INTO `django_content_type` VALUES (3, 'auth', 'permission');
INSERT INTO `django_content_type` VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES (14, 'devices', 'device');
INSERT INTO `django_content_type` VALUES (8, 'parking', 'parkingsession');
INSERT INTO `django_content_type` VALUES (19, 'parking', 'parkingspace');
INSERT INTO `django_content_type` VALUES (9, 'parking', 'parkingspot');
INSERT INTO `django_content_type` VALUES (10, 'parking', 'reservation');
INSERT INTO `django_content_type` VALUES (18, 'parking', 'spotconnection');
INSERT INTO `django_content_type` VALUES (23, 'payments', 'bankcard');
INSERT INTO `django_content_type` VALUES (11, 'payments', 'payment');
INSERT INTO `django_content_type` VALUES (12, 'payments', 'pricingrule');
INSERT INTO `django_content_type` VALUES (13, 'payments', 'subscription');
INSERT INTO `django_content_type` VALUES (22, 'payments', 'subscriptionplan');
INSERT INTO `django_content_type` VALUES (20, 'payments', 'topuprecord');
INSERT INTO `django_content_type` VALUES (21, 'payments', 'userbalance');
INSERT INTO `django_content_type` VALUES (5, 'sessions', 'session');

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 58 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO `django_migrations` VALUES (1, 'contenttypes', '0001_initial', '2026-04-12 18:42:19.409767');
INSERT INTO `django_migrations` VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2026-04-12 18:42:19.470534');
INSERT INTO `django_migrations` VALUES (3, 'auth', '0001_initial', '2026-04-12 18:42:19.740818');
INSERT INTO `django_migrations` VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2026-04-12 18:42:19.798356');
INSERT INTO `django_migrations` VALUES (5, 'auth', '0003_alter_user_email_max_length', '2026-04-12 18:42:19.804913');
INSERT INTO `django_migrations` VALUES (6, 'auth', '0004_alter_user_username_opts', '2026-04-12 18:42:19.809648');
INSERT INTO `django_migrations` VALUES (7, 'auth', '0005_alter_user_last_login_null', '2026-04-12 18:42:19.814341');
INSERT INTO `django_migrations` VALUES (8, 'auth', '0006_require_contenttypes_0002', '2026-04-12 18:42:19.817549');
INSERT INTO `django_migrations` VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2026-04-12 18:42:19.822287');
INSERT INTO `django_migrations` VALUES (10, 'auth', '0008_alter_user_username_max_length', '2026-04-12 18:42:19.824514');
INSERT INTO `django_migrations` VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2026-04-12 18:42:19.831762');
INSERT INTO `django_migrations` VALUES (12, 'auth', '0010_alter_group_name_max_length', '2026-04-12 18:42:19.846123');
INSERT INTO `django_migrations` VALUES (13, 'auth', '0011_update_proxy_permissions', '2026-04-12 18:42:19.851977');
INSERT INTO `django_migrations` VALUES (14, 'auth', '0012_alter_user_first_name_max_length', '2026-04-12 18:42:19.857355');
INSERT INTO `django_migrations` VALUES (15, 'accounts', '0001_initial', '2026-04-12 18:42:20.234436');
INSERT INTO `django_migrations` VALUES (16, 'admin', '0001_initial', '2026-04-12 18:42:20.354878');
INSERT INTO `django_migrations` VALUES (17, 'admin', '0002_logentry_remove_auto_add', '2026-04-12 18:42:20.361082');
INSERT INTO `django_migrations` VALUES (18, 'admin', '0003_logentry_add_action_flag_choices', '2026-04-12 18:42:20.366879');
INSERT INTO `django_migrations` VALUES (19, 'alerts', '0001_initial', '2026-04-12 18:42:20.462513');
INSERT INTO `django_migrations` VALUES (20, 'devices', '0001_initial', '2026-04-12 18:42:20.488234');
INSERT INTO `django_migrations` VALUES (21, 'parking', '0001_initial', '2026-04-12 18:42:20.746506');
INSERT INTO `django_migrations` VALUES (22, 'payments', '0001_initial', '2026-04-12 18:42:20.965931');
INSERT INTO `django_migrations` VALUES (23, 'sessions', '0001_initial', '2026-04-12 18:42:20.996729');
INSERT INTO `django_migrations` VALUES (24, 'accounts', '0002_user_totp_secret_user_two_factor_enabled', '2026-04-13 04:45:52.727102');
INSERT INTO `django_migrations` VALUES (25, 'ai_recognition', '0001_initial', '2026-04-14 13:55:10.551236');
INSERT INTO `django_migrations` VALUES (26, 'ai_recognition', '0002_alter_recognitionrecord_action_taken', '2026-04-15 17:28:20.736723');
INSERT INTO `django_migrations` VALUES (27, 'parking', '0002_spotconnection', '2026-04-18 16:38:52.247581');
INSERT INTO `django_migrations` VALUES (28, 'ai_recognition', '0003_remove_recognitionrecord_image_and_more', '2026-04-18 17:23:32.375452');
INSERT INTO `django_migrations` VALUES (29, 'parking', '0003_parkingspace', '2026-04-19 03:35:01.094349');
INSERT INTO `django_migrations` VALUES (30, 'parking', '0004_parkingspace_qr_code_token', '2026-04-19 03:42:37.040667');
INSERT INTO `django_migrations` VALUES (31, 'parking', '0005_add_b_floors', '2026-04-19 06:27:53.889299');
INSERT INTO `django_migrations` VALUES (32, 'parking', '0006_alter_parkingspace_options_and_more', '2026-04-19 08:49:40.263969');
INSERT INTO `django_migrations` VALUES (33, 'parking', '0007_parkingspace_rotation', '2026-04-19 09:50:21.963098');
INSERT INTO `django_migrations` VALUES (34, 'parking', '0008_parkingspace_type', '2026-04-19 11:31:22.684171');
INSERT INTO `django_migrations` VALUES (35, 'parking', '0009_alter_parkingspace_status_bool', '2026-04-19 11:52:07.133587');
INSERT INTO `django_migrations` VALUES (36, 'parking', '0010_parkingspace_is_reserved', '2026-04-19 13:45:36.255937');
INSERT INTO `django_migrations` VALUES (37, 'parking', '0011_parkingspace_reserved_plate', '2026-04-19 14:17:49.214551');
INSERT INTO `django_migrations` VALUES (38, 'payments', '0002_add_userbalance_topuprecord', '2026-04-19 15:39:48.835055');
INSERT INTO `django_migrations` VALUES (39, 'payments', '0003_subscription_plan_table', '2026-04-19 16:09:16.760509');
INSERT INTO `django_migrations` VALUES (40, 'payments', '0004_subscription_plan_recommended', '2026-04-19 16:31:11.824651');
INSERT INTO `django_migrations` VALUES (41, 'parking', '0012_remove_legacy_parkingspot', '2026-04-19 16:49:43.167725');
INSERT INTO `django_migrations` VALUES (42, 'payments', '0005_pricing_rule_reservation', '2026-04-19 17:11:39.281066');
INSERT INTO `django_migrations` VALUES (43, 'parking', '0013_add_reservation_end_date', '2026-04-19 17:14:55.186449');
INSERT INTO `django_migrations` VALUES (44, 'parking', '0014_reservation_payment_fields', '2026-04-20 04:25:19.822725');
INSERT INTO `django_migrations` VALUES (45, 'parking', '0015_remove_parkingspace_is_reserved', '2026-04-20 06:57:26.199792');
INSERT INTO `django_migrations` VALUES (46, 'payments', '0006_bankcard', '2026-04-20 15:10:42.738540');
INSERT INTO `django_migrations` VALUES (47, 'parking', '0016_parkingspace_navigation_start_fields', '2026-04-26 12:37:25.359554');
INSERT INTO `django_migrations` VALUES (48, 'parking', '0017_parking_space_node_type_and_location_name', '2026-04-26 12:52:06.908368');
INSERT INTO `django_migrations` VALUES (49, 'accounts', '0003_remove_user_user_permissions', '2026-05-04 16:51:13.106563');
INSERT INTO `django_migrations` VALUES (50, 'accounts', '0004_drop_alert_tables', '2026-05-04 16:51:13.156611');
INSERT INTO `django_migrations` VALUES (51, 'accounts', '0005_add_vehicle_is_simulated', '2026-05-06 08:42:53.335301');
INSERT INTO `django_migrations` VALUES (53, 'parking', '0018_add_public_locations', '2026-05-06 13:29:29.558112');
INSERT INTO `django_migrations` VALUES (54, 'parking', '0019_alter_reservation_options_and_more', '2026-05-06 16:07:16.294087');
INSERT INTO `django_migrations` VALUES (55, 'payments', '0007_add_biz_type', '2026-05-07 05:56:09.472752');
INSERT INTO `django_migrations` VALUES (56, 'payments', '0008_add_pricing_rule_types', '2026-05-07 09:51:45.846826');
INSERT INTO `django_migrations` VALUES (57, 'payments', '0009_add_default_pricing_rules', '2026-05-07 09:51:45.878217');

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session`  (
  `session_key` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `session_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`) USING BTREE,
  INDEX `django_session_expire_date_a5c62663`(`expire_date` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_session
-- ----------------------------
INSERT INTO `django_session` VALUES ('0vv1jnjoqod5sp10uaklz2zn96yyni06', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr8r:TiGhBmil445yZcCcp8V5dakwfQJSs1JYMFW65Z4n97I', '2026-05-04 16:06:33.225721');
INSERT INTO `django_session` VALUES ('26dx89vt3cwaiub2ahbok4mms5km8a4o', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr9D:7muOfvI2xbxkoo3-Bbed0fwffKYCpIvhW5McMvse92g', '2026-05-04 16:06:55.207458');
INSERT INTO `django_session` VALUES ('2fpd5vjkayf8szbc699bra3yabatospd', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqjq:YOS66mnZRdo0c96Wg-zElDFDaSY8fXtgnkUDwI8Ht5M', '2026-05-04 15:40:42.142861');
INSERT INTO `django_session` VALUES ('30cwrfgjytfnm77ovzcy2xlm4tko5ka8', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr15:WGiWQtqlBz9u9fXuaedR92unreiNdGWZfPCODKnd1fY', '2026-05-04 15:58:31.277554');
INSERT INTO `django_session` VALUES ('4c79y4hcrkj6mcbwhmkglh6kfmeqn9rq', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqlE:5W5cgf5htDL1PaU0j-prs5OqveQmwuyBy7Ci1CYU-uw', '2026-05-04 15:42:08.843476');
INSERT INTO `django_session` VALUES ('4hfiteo219324ceiifl47h9muonzsdxi', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqdw:jrpn7kUv_1et3N-Po_MLnAiwlRjOch_4YVLoMacOJCA', '2026-05-04 15:34:36.640675');
INSERT INTO `django_session` VALUES ('4hxy3am1m3e3n5bwgsu4bmr5aao1jwwp', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqm9:FsVNYKvBzY7BzI5JWvu-Rtje3AMI1u5a3IerYrgdlcc', '2026-05-04 15:43:05.043699');
INSERT INTO `django_session` VALUES ('7okm289n2a4xxci6d4yyftqnt2opf02g', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqrv:f-jQQnIT1GgLuHt0pGx_mT63wds5QBgKrdZ8_b8nnE0', '2026-05-04 15:49:03.552022');
INSERT INTO `django_session` VALUES ('9vnyv0izug62o9idz2krl1d4tqhva56k', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqgh:-BANeJWTDDx_JBLjkJfnVb2u8d9wrbCzrGntMMUTWYY', '2026-05-04 15:37:27.724322');
INSERT INTO `django_session` VALUES ('a882q32b9h2xqr8o6nr6i0olk4tcdbt8', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr1U:drC5XY0iXGngLaduP3hMMdPMCOrZQ0R7FwP5Kyl3G6s', '2026-05-04 15:58:56.056146');
INSERT INTO `django_session` VALUES ('aywv2g8ys9kivm85tsgs95lzzh42r2a7', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqdV:kIh1JzBLjFZ9p0_s08WuNgGJInrKprkWBl-rDqSUjkk', '2026-05-04 15:34:09.224699');
INSERT INTO `django_session` VALUES ('bbf47onsx1apvp7g3j1ei4yr3wuyp6au', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr4W:A0-vGcYVROoiLJffQadQCgWzDQNz4dHMPkoCoFU1TL8', '2026-05-04 16:02:04.394133');
INSERT INTO `django_session` VALUES ('cjpt8x2odzo5drhztx3kzgm0oov4hwic', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqbT:4-Qy0OkDqzJjvji0DknesMQwQNtatB3TjGmQ3jaMNqs', '2026-05-04 15:32:03.846929');
INSERT INTO `django_session` VALUES ('ejyuj6zroceig0cxgcwtzfcuirqhykbn', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqrZ:YspOXorNlW4rRVC1HFmaqdnZaLv1XRu3KFEH9QKuXPc', '2026-05-04 15:48:41.999680');
INSERT INTO `django_session` VALUES ('emrbplvp2vnupjm94b3bzbkwbq7yaj0t', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqpS:yxCrVtw-uVIxjZ_uUKzDC-E53g6b_FNIVEJnw7fNWh8', '2026-05-04 15:46:30.567541');
INSERT INTO `django_session` VALUES ('fi8z7h73ih2usvu4atznhhl55ap4od33', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqol:o5nX4YIxnrwNPNHzH5kaoS5mY6U22NbjV2Mw6mfLWqw', '2026-05-04 15:45:47.450508');
INSERT INTO `django_session` VALUES ('hqmpyqohxlv87z8i7opfodbpajig3g0i', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr0u:hzI5MoP6dSPFZbZzZZr1oHBmWuf9Np07KUriR8wU71s', '2026-05-04 15:58:20.068829');
INSERT INTO `django_session` VALUES ('lp1aol1lhctnkikjkxkp0atabwxycgnu', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr1g:jgxxD_7YKIzfTQKlJ27XuzzgFzMNIoMaM7xtfqytY2A', '2026-05-04 15:59:08.630500');
INSERT INTO `django_session` VALUES ('m2if3l7pinamlz20ur4n8zjm60vrk754', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr8Z:UH_e9H-aqJcWaYTGhgOTDZ6_eS9rH4x-l5QWxhvWG_8', '2026-05-04 16:06:15.945901');
INSERT INTO `django_session` VALUES ('mfstwf7zp0rmr5vmrfvzgqtusldj04yj', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr7t:ix5_8ACl5B5Bk-QyJNfH-SGZGrqJnG8iIjadIBYmceg', '2026-05-04 16:05:33.828045');
INSERT INTO `django_session` VALUES ('n6njme4ooy4z6yezcfzf6zdf07ohvitz', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqbI:iK7DXuEeL2AeoOlaGVtnVWScBbYXJr4VBa8wDCVuZQk', '2026-05-04 15:31:52.148167');
INSERT INTO `django_session` VALUES ('o4afy12rslff2so4j3phbly20q314skr', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr8C:9ECDD7rUCDFMm_19EBXWdlZrdw9DBHEqAYB6CmUX6Qo', '2026-05-04 16:05:52.539917');
INSERT INTO `django_session` VALUES ('u78cp6oask4613uw6vw66oomt1wq4n5g', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr0j:VhmSfJqvB4b_SCY2VmUFyu0BReq-93nsIZ8Ab8HVs-E', '2026-05-04 15:58:09.407201');
INSERT INTO `django_session` VALUES ('w56svwhb60c5ytsqrq7z6cbvbd4bum0g', '.eJxVjEEOwiAQRe_C2pAOjEBduu8ZCAODVA0kpV0Z765NutDtf-_9l_BhW4vfOi9-TuIiQIvT70ghPrjuJN1DvTUZW12XmeSuyIN2ObXEz-vh_h2U0Mu3zk45tsSYFCJwzBrR2jE67QwnGvN5sE5FBUEbo4AMJgMEbAeD2iKI9wf9YDci:1wEoTG:CGMsNFdzvIkg0dmTN8mPS7u7aq8CHzIKQ182_uSHL2w', '2026-05-04 13:15:26.272422');
INSERT INTO `django_session` VALUES ('yy5ffag7t3b1yxaj6t837dtcvo6qfjes', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEqgV:BRKFFmjLPTuPpw078kYp-0e1plIaikvuPVqu7oDWHHM', '2026-05-04 15:37:15.878741');
INSERT INTO `django_session` VALUES ('zyt9vawe2xnb1vir0bgz73jh7p2izntw', '.eJxVjEEOgjAQRe_StWkoTJnWpXvPQGamU4saSCisjHdXEha6_e-9_zIDbWsZtqrLMCZzNs6cfjcmeei0g3Sn6TZbmad1Gdnuij1otdc56fNyuH8HhWr51r4FH2MEAsSu00BOlCFIwwCSEZJy8owBIUeNjNiqZN_0jqDrmxTN-wPWEje_:1wEr2Q:OenvgTohz3i8VscJj7lH85gDeguj3N7nxhkMWkoxV3s', '2026-05-04 15:59:54.659833');

-- ----------------------------
-- Table structure for parking_space
-- ----------------------------
DROP TABLE IF EXISTS `parking_space`;
CREATE TABLE `parking_space`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `space_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` tinyint(1) NOT NULL,
  `current_plate` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `last_updated` datetime(6) NOT NULL,
  `center_x` double NULL DEFAULT NULL,
  `center_y` double NULL DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `qr_code_token` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `bind_time` datetime(6) NULL DEFAULT NULL,
  `x` double NULL DEFAULT NULL,
  `y` double NULL DEFAULT NULL,
  `floor` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `rotation` int NOT NULL,
  `type` tinyint(1) NOT NULL,
  `reserved_plate` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `node_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `location_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `pending_exit_plate` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `pending_exit_time` datetime(6) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `qr_code_token`(`qr_code_token` ASC) USING BTREE,
  UNIQUE INDEX `parking_space_floor_space_id_85b67e5a_uniq`(`floor` ASC, `space_id` ASC) USING BTREE,
  INDEX `parking_spa_floor_ff724f_idx`(`floor` ASC, `status` ASC) USING BTREE,
  INDEX `parking_spa_floor_0b7424_idx`(`floor` ASC, `current_plate` ASC) USING BTREE,
  INDEX `parking_spa_node_ty_1ae00c_idx`(`node_type` ASC, `floor` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1208 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of parking_space
-- ----------------------------
INSERT INTO `parking_space` VALUES (521, 'space_A001', 0, '苏D3Q520', '2026-05-07 10:20:46.432555', 196.2835, 326.7775, '2026-05-05 15:07:26.274929', 'QR_SPACE_A001', NULL, 172.9835, 287.5775, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (522, 'space_A002', 0, '京A10002', '2026-05-05 15:07:26.273930', 196.2835, 409.3785, '2026-05-05 15:07:26.274929', 'QR_SPACE_A002', '2026-04-19 05:32:21.559564', 172.9835, 370.1785, 'B2', 0, 0, NULL, 'parking', '', '京A10002', '2026-05-06 16:19:35.617840');
INSERT INTO `parking_space` VALUES (523, 'space_A003', 0, '鲁B325DE', '2026-05-07 10:20:48.406694', 247.48250000000002, 326.7775, '2026-05-05 15:07:26.274929', 'QR_SPACE_A003', NULL, 224.1825, 287.5775, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (524, 'space_A004', 0, '京A10004', '2026-05-05 15:07:26.273930', 247.48250000000002, 409.3785, '2026-05-05 15:07:26.274929', 'QR_SPACE_A004', '2026-04-19 05:32:21.559564', 224.1825, 370.1785, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (525, 'space_A005', 0, '京A10005', '2026-05-05 15:07:26.273930', 298.6825, 326.7775, '2026-05-05 15:07:26.274929', 'QR_SPACE_A005', '2026-04-19 05:32:21.559564', 275.3825, 287.5775, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (526, 'space_A006', 0, '京A10006', '2026-05-05 15:07:26.273930', 298.6825, 409.3785, '2026-05-05 15:07:26.274929', 'QR_SPACE_A006', '2026-04-19 05:32:21.559564', 275.3825, 370.1785, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (527, 'space_A007', 0, '京A10007', '2026-05-05 15:07:26.273930', 349.8815, 326.7775, '2026-05-05 15:07:26.274929', 'QR_SPACE_A007', '2026-04-19 05:32:21.559564', 326.5815, 287.5775, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (528, 'space_A008', 0, '', '2026-05-07 10:20:46.538874', 349.8815, 409.3785, '2026-05-05 15:07:26.274929', 'QR_SPACE_A008', NULL, 326.5815, 370.1785, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (529, 'space_A009', 0, '京A10009', '2026-05-05 15:07:26.273930', 401.08050000000003, 326.7775, '2026-05-05 15:07:26.274929', 'QR_SPACE_A009', '2026-04-19 05:32:21.559564', 377.7805, 287.5775, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (530, 'space_A010', 0, '京A10010', '2026-05-05 15:07:26.273930', 401.08050000000003, 409.3785, '2026-05-05 15:07:26.274929', 'QR_SPACE_A010', '2026-04-19 05:32:21.559564', 377.7805, 370.1785, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (531, 'space_A011', 0, '京A10011', '2026-05-05 15:07:26.273930', 452.27950000000004, 326.7775, '2026-05-05 15:07:26.274929', 'QR_SPACE_A011', '2026-04-19 05:32:21.559564', 428.97950000000003, 287.5775, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (532, 'space_A012', 0, '京A10012', '2026-05-05 15:07:26.273930', 452.27950000000004, 409.5475, '2026-05-05 15:07:26.274929', 'QR_SPACE_A012', '2026-04-19 05:32:21.559564', 428.97950000000003, 370.3475, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (533, 'space_A013', 0, '京A10013', '2026-05-05 15:07:26.273930', 196.28650000000002, 583.6215000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A013', '2026-04-19 05:32:21.559564', 172.9865, 544.4215, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (534, 'space_A014', 0, '京A10014', '2026-05-05 15:07:26.273930', 247.4865, 583.6215000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A014', '2026-04-19 05:32:21.559564', 224.1865, 544.4215, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (535, 'space_A015', 0, '京A10015', '2026-05-05 15:07:26.273930', 298.6865, 583.6215000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A015', '2026-04-19 05:32:21.559564', 275.3865, 544.4215, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (536, 'space_A016', 0, '京A10016', '2026-05-05 15:07:26.273930', 349.8865, 583.6215000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A016', '2026-04-19 05:32:21.559564', 326.5865, 544.4215, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (537, 'space_A017', 0, '京A10017', '2026-05-05 15:07:26.273930', 401.0865, 583.6215000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A017', '2026-04-19 05:32:21.559564', 377.7865, 544.4215, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (538, 'space_A018', 0, '京A10018', '2026-05-05 15:07:26.273930', 452.2765, 583.7905000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A018', '2026-04-19 05:32:21.559564', 428.9765, 544.5905, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (539, 'space_A019', 0, NULL, '2026-05-05 15:07:26.273930', 513.3955, 326.8625, '2026-05-05 15:07:26.274929', 'QR_SPACE_A019', NULL, 490.0955, 287.6625, 'B2', 0, 0, '豫R8JU93', 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (540, 'space_A020', 0, '', '2026-05-07 10:20:26.394137', 513.3955, 409.4635, '2026-05-05 15:07:26.274929', 'QR_SPACE_A020', NULL, 490.0955, 370.2635, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (541, 'space_A021', 0, NULL, '2026-05-05 15:07:26.273930', 564.5955, 326.8625, '2026-05-05 15:07:26.274929', 'QR_SPACE_A021', NULL, 541.2955000000001, 287.6625, 'B2', 0, 0, '沪B0D955', 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (542, 'space_A022', 0, '', '2026-05-07 10:20:48.574896', 564.5955, 409.4635, '2026-05-05 15:07:26.274929', 'QR_SPACE_A022', NULL, 541.2955000000001, 370.2635, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (543, 'space_A023', 0, '苏AGN567', '2026-05-07 09:37:39.606100', 615.7955, 326.8625, '2026-05-05 15:07:26.274929', 'QR_SPACE_A023', NULL, 592.4955, 287.6625, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (544, 'space_A024', 0, '', '2026-05-06 08:39:53.450740', 615.7955, 409.4635, '2026-05-05 15:07:26.274929', 'QR_SPACE_A024', NULL, 592.4955, 370.2635, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (545, 'space_A025', 0, NULL, '2026-05-05 15:07:26.273930', 666.9955, 326.8625, '2026-05-05 15:07:26.274929', 'QR_SPACE_A025', NULL, 643.6955, 287.6625, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (546, 'space_A026', 0, '浙A28001', '2026-05-07 10:20:26.580060', 666.9955, 409.4635, '2026-05-05 15:07:26.274929', 'QR_SPACE_A026', NULL, 643.6955, 370.2635, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (547, 'space_A027', 0, NULL, '2026-05-05 15:07:26.273930', 718.1954999999999, 326.8625, '2026-05-05 15:07:26.274929', 'QR_SPACE_A027', NULL, 694.8955, 287.6625, 'B2', 0, 0, '沪BBTF81', 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (548, 'space_A028', 0, NULL, '2026-05-05 15:07:26.273930', 718.1954999999999, 409.4635, '2026-05-05 15:07:26.274929', 'QR_SPACE_A028', NULL, 694.8955, 370.2635, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (549, 'space_A029', 0, '新AD1ILO', '2026-05-07 10:20:46.701969', 769.3855, 326.8625, '2026-05-05 15:07:26.274929', 'QR_SPACE_A029', NULL, 746.0855, 287.6625, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (550, 'space_A030', 0, NULL, '2026-05-05 15:07:26.273930', 769.3855, 409.6325, '2026-05-05 15:07:26.274929', 'QR_SPACE_A030', NULL, 746.0855, 370.4325, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (551, 'space_A031', 0, '浙ASB886', '2026-05-07 09:38:07.472477', 237.9035, 86.4992, '2026-05-05 15:07:26.274929', 'QR_SPACE_A031', NULL, 214.6035, 47.2992, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (552, 'space_A032', 0, '', '2026-05-07 10:20:48.460886', 289.1035, 86.4992, '2026-05-05 15:07:26.274929', 'QR_SPACE_A032', NULL, 265.8035, 47.2992, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (553, 'space_A033', 0, '新AD1ILO', '2026-05-07 10:20:26.759633', 340.30350000000004, 86.4992, '2026-05-05 15:07:26.274929', 'QR_SPACE_A033', NULL, 317.00350000000003, 47.2992, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (554, 'space_A034', 0, '川A42344', '2026-05-07 10:20:26.698800', 391.50350000000003, 86.4992, '2026-05-05 15:07:26.274929', 'QR_SPACE_A034', NULL, 368.2035, 47.2992, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (555, 'space_A035', 0, NULL, '2026-05-05 15:07:26.273930', 442.7035, 86.4992, '2026-05-05 15:07:26.274929', 'QR_SPACE_A035', NULL, 419.4035, 47.2992, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (556, 'space_A036', 0, '京A51134', '2026-05-05 15:07:26.273930', 493.8935, 86.4992, '2026-05-05 15:07:26.274929', 'QR_SPACE_A036', '2026-04-19 05:38:22.454534', 470.5935, 47.2992, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (557, 'space_A048', 0, '', '2026-05-07 10:20:46.809071', 513.3955, 583.9725000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A048', NULL, 490.0955, 544.7725, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (558, 'space_A049', 0, '川A42344', '2026-05-07 10:20:46.643613', 564.5955, 583.9725000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A049', NULL, 541.2955000000001, 544.7725, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (559, 'space_A050', 0, NULL, '2026-05-05 15:07:26.274929', 615.7955, 583.9725000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A050', NULL, 592.4955, 544.7725, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (560, 'space_A051', 0, NULL, '2026-05-05 15:07:26.274929', 666.9955, 583.9725000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A051', NULL, 643.6955, 544.7725, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (561, 'space_A052', 0, '粤R8888R', '2026-05-07 10:20:46.591000', 718.1954999999999, 583.9725000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A052', NULL, 694.8955, 544.7725, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (562, 'space_A053', 0, NULL, '2026-05-05 15:07:26.274929', 769.3855, 584.1415000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A053', NULL, 746.0855, 544.9415, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (563, 'space_A054', 0, '', '2026-05-07 10:20:46.484882', 196.2845, 665.1765, '2026-05-05 15:07:26.274929', 'QR_SPACE_A054', NULL, 172.9845, 625.9765, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (564, 'space_A055', 0, NULL, '2026-05-05 15:07:26.274929', 247.48450000000003, 665.1765, '2026-05-05 15:07:26.274929', 'QR_SPACE_A055', NULL, 224.1845, 625.9765, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (565, 'space_A056', 0, NULL, '2026-05-05 15:07:26.274929', 298.6845, 665.1765, '2026-05-05 15:07:26.274929', 'QR_SPACE_A056', NULL, 275.3845, 625.9765, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (566, 'space_A057', 0, '', '2026-05-07 10:20:48.687534', 349.8845, 665.1765, '2026-05-05 15:07:26.274929', 'QR_SPACE_A057', NULL, 326.5845, 625.9765, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (567, 'space_A058', 0, NULL, '2026-05-05 15:07:26.274929', 401.0845, 665.1765, '2026-05-05 15:07:26.274929', 'QR_SPACE_A058', NULL, 377.7845, 625.9765, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (568, 'space_A059', 0, '', '2026-05-07 10:20:26.871864', 452.2745, 665.3455, '2026-05-05 15:07:26.274929', 'QR_SPACE_A059', NULL, 428.9745, 626.1455, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (569, 'space_A060', 0, '', '2026-05-07 10:20:26.637452', 513.3945, 665.2615000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A060', NULL, 490.09450000000004, 626.0615, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (570, 'space_A061', 0, '', '2026-05-07 10:20:48.802231', 564.5944999999999, 665.2615000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A061', NULL, 541.2945, 626.0615, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (571, 'space_A062', 0, NULL, '2026-05-05 15:07:26.274929', 615.7945, 665.2615000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A062', NULL, 592.4945, 626.0615, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (572, 'space_A063', 0, NULL, '2026-05-05 15:07:26.274929', 666.9944999999999, 665.2615000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A063', NULL, 643.6945, 626.0615, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (573, 'space_A064', 0, '', '2026-05-07 10:20:26.460373', 718.1945, 665.2615000000001, '2026-05-05 15:07:26.274929', 'QR_SPACE_A064', NULL, 694.8945, 626.0615, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (574, 'space_A065', 0, '', '2026-05-07 10:20:46.379062', 769.3845, 665.4305, '2026-05-05 15:07:26.274929', 'QR_SPACE_A065', NULL, 746.0845, 626.2305, 'B2', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (683, 'space_A037', 0, '新AD1ILO', '2026-05-06 08:45:27.100578', 993.0155, 351.39549999999997, '2026-05-05 15:07:26.274929', 'QR_SPACE_A037', NULL, 969.7155, 312.1955, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (684, 'space_A038', 0, '', '2026-05-07 10:20:48.746554', 993.0155, 300.1955, '2026-05-05 15:07:26.274929', 'QR_SPACE_A038', NULL, 969.7155, 260.9955, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (685, 'space_A039', 0, '', '2026-05-07 10:20:26.815562', 993.0155, 249.00549999999998, '2026-05-05 15:07:26.274929', 'QR_SPACE_A039', NULL, 969.7155, 209.8055, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (686, 'space_A040', 0, '沪AD55320', '2026-05-05 15:07:26.274929', 993.0155, 516.0155, '2026-05-05 15:07:26.274929', 'QR_SPACE_A040', '2026-04-19 05:34:49.770390', 969.7155, 476.8155, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (687, 'space_A041', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 464.8155, '2026-05-05 15:07:26.276434', 'QR_SPACE_A041', NULL, 969.7155, 425.6155, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (688, 'space_A042', 0, '', '2026-05-07 10:20:48.629289', 993.0155, 413.6255, '2026-05-05 15:07:26.276434', 'QR_SPACE_A042', NULL, 969.7155, 374.4255, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (689, 'space_A043', 0, '粤AD76278', '2026-05-05 15:07:26.274929', 993.0155, 680.2005, '2026-05-05 15:07:26.276434', 'QR_SPACE_A043', '2026-04-19 05:34:49.770390', 969.7155, 641.0005, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (690, 'space_A044', 0, '', '2026-05-07 10:20:46.760674', 993.0155, 629.0005000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_A044', NULL, 969.7155, 589.8005, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (691, 'space_A045', 0, '', '2026-05-07 10:20:48.512637', 993.0155, 577.8105, '2026-05-05 15:07:26.276434', 'QR_SPACE_A045', NULL, 969.7155, 538.6105, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (692, 'space_A046', 0, '', '2026-05-07 10:20:26.520214', 993.0155, 792.5505, '2026-05-05 15:07:26.276434', 'QR_SPACE_A046', NULL, 969.7155, 753.3505, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (693, 'space_A047', 1, NULL, '2026-05-05 15:07:26.274929', 993.0155, 741.3505, '2026-05-05 15:07:26.276434', 'QR_SPACE_A047', NULL, 969.7155, 702.1505, 'B2', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (716, 'space_B001', 0, NULL, '2026-05-05 15:07:26.274929', 196.2835, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_B001', NULL, 172.9835, 287.5775, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (717, 'space_B002', 0, NULL, '2026-05-05 15:07:26.274929', 196.2835, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_B002', NULL, 172.9835, 370.1785, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (718, 'space_B003', 0, '粤C52217', '2026-05-05 15:07:26.274929', 247.48250000000002, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_B003', '2026-04-19 05:38:22.454534', 224.1825, 287.5775, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (719, 'space_B004', 0, NULL, '2026-05-05 15:07:26.274929', 247.48250000000002, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_B004', NULL, 224.1825, 370.1785, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (720, 'space_B005', 0, NULL, '2026-05-05 15:07:26.274929', 298.6825, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_B005', NULL, 275.3825, 287.5775, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (721, 'space_B006', 0, NULL, '2026-05-05 15:07:26.274929', 298.6825, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_B006', NULL, 275.3825, 370.1785, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (722, 'space_B007', 0, NULL, '2026-05-05 15:07:26.274929', 349.8815, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_B007', NULL, 326.5815, 287.5775, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (723, 'space_B008', 0, NULL, '2026-05-05 15:07:26.274929', 349.8815, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_B008', NULL, 326.5815, 370.1785, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (724, 'space_B009', 0, '京A12072', '2026-05-05 15:07:26.274929', 401.08050000000003, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_B009', '2026-04-19 05:38:22.454534', 377.7805, 287.5775, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (725, 'space_B010', 0, NULL, '2026-05-05 15:07:26.274929', 401.08050000000003, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_B010', NULL, 377.7805, 370.1785, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (726, 'space_B011', 0, NULL, '2026-05-05 15:07:26.274929', 452.27950000000004, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_B011', NULL, 428.97950000000003, 287.5775, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (727, 'space_B012', 0, '粤C89646', '2026-05-05 15:07:26.274929', 452.27950000000004, 409.5475, '2026-05-05 15:07:26.276434', 'QR_SPACE_B012', '2026-04-19 05:38:22.454534', 428.97950000000003, 370.3475, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (728, 'space_B013', 0, NULL, '2026-05-05 15:07:26.274929', 196.28650000000002, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B013', NULL, 172.9865, 544.4215, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (729, 'space_B014', 0, NULL, '2026-05-05 15:07:26.274929', 247.4865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B014', NULL, 224.1865, 544.4215, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (730, 'space_B015', 0, NULL, '2026-05-05 15:07:26.274929', 298.6865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B015', NULL, 275.3865, 544.4215, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (731, 'space_B016', 0, NULL, '2026-05-05 15:07:26.274929', 349.8865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B016', NULL, 326.5865, 544.4215, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (732, 'space_B017', 0, NULL, '2026-05-05 15:07:26.274929', 401.0865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B017', NULL, 377.7865, 544.4215, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (733, 'space_B018', 0, '京A72847', '2026-05-05 15:07:26.274929', 452.2765, 583.7905000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B018', '2026-04-19 05:38:22.454534', 428.9765, 544.5905, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (734, 'space_B019', 0, NULL, '2026-05-05 15:07:26.274929', 513.3955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_B019', NULL, 490.0955, 287.6625, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (735, 'space_B020', 0, NULL, '2026-05-05 15:07:26.274929', 513.3955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_B020', NULL, 490.0955, 370.2635, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (736, 'space_B021', 0, NULL, '2026-05-05 15:07:26.274929', 564.5955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_B021', NULL, 541.2955000000001, 287.6625, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (737, 'space_B022', 0, NULL, '2026-05-05 15:07:26.274929', 564.5955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_B022', NULL, 541.2955000000001, 370.2635, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (738, 'space_B023', 0, NULL, '2026-05-05 15:07:26.274929', 615.7955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_B023', NULL, 592.4955, 287.6625, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (739, 'space_B024', 0, NULL, '2026-05-05 15:07:26.274929', 615.7955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_B024', NULL, 592.4955, 370.2635, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (740, 'space_B025', 0, NULL, '2026-05-05 15:07:26.274929', 666.9955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_B025', NULL, 643.6955, 287.6625, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (741, 'space_B026', 0, NULL, '2026-05-05 15:07:26.274929', 666.9955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_B026', NULL, 643.6955, 370.2635, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (742, 'space_B027', 0, NULL, '2026-05-05 15:07:26.274929', 718.1954999999999, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_B027', NULL, 694.8955, 287.6625, 'B1', 0, 0, '京AH47SB', 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (743, 'space_B028', 0, NULL, '2026-05-05 15:07:26.274929', 718.1954999999999, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_B028', NULL, 694.8955, 370.2635, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (744, 'space_B029', 0, NULL, '2026-05-05 15:07:26.274929', 769.3855, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_B029', NULL, 746.0855, 287.6625, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (745, 'space_B030', 0, NULL, '2026-05-05 15:07:26.274929', 769.3855, 409.6325, '2026-05-05 15:07:26.276434', 'QR_SPACE_B030', NULL, 746.0855, 370.4325, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (746, 'space_B031', 0, '京A68093', '2026-05-05 15:07:26.274929', 237.9035, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_B031', '2026-04-19 05:38:22.454534', 214.6035, 47.2992, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (747, 'space_B032', 0, NULL, '2026-05-05 15:07:26.274929', 289.1035, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_B032', NULL, 265.8035, 47.2992, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (748, 'space_B033', 0, NULL, '2026-05-05 15:07:26.274929', 340.30350000000004, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_B033', NULL, 317.00350000000003, 47.2992, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (749, 'space_B034', 0, '京A04328', '2026-05-05 15:07:26.274929', 391.50350000000003, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_B034', '2026-04-19 05:38:22.454534', 368.2035, 47.2992, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (750, 'space_B035', 0, NULL, '2026-05-05 15:07:26.274929', 442.7035, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_B035', NULL, 419.4035, 47.2992, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (751, 'space_B036', 0, NULL, '2026-05-05 15:07:26.274929', 493.8935, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_B036', NULL, 470.5935, 47.2992, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (752, 'space_B037', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 351.39549999999997, '2026-05-05 15:07:26.276434', 'QR_SPACE_B037', NULL, 969.7155, 312.1955, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (753, 'space_B038', 0, '粤AD66568', '2026-05-05 15:07:26.274929', 993.0155, 300.1955, '2026-05-05 15:07:26.276434', 'QR_SPACE_B038', '2026-04-19 05:34:49.770390', 969.7155, 260.9955, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (754, 'space_B039', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 249.00549999999998, '2026-05-05 15:07:26.276434', 'QR_SPACE_B039', NULL, 969.7155, 209.8055, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (755, 'space_B040', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 516.0155, '2026-05-05 15:07:26.276434', 'QR_SPACE_B040', NULL, 969.7155, 476.8155, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (756, 'space_B041', 0, '沪AD80653', '2026-05-05 15:07:26.274929', 993.0155, 464.8155, '2026-05-05 15:07:26.276434', 'QR_SPACE_B041', '2026-04-19 05:34:49.770390', 969.7155, 425.6155, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (757, 'space_B042', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 413.6255, '2026-05-05 15:07:26.276434', 'QR_SPACE_B042', NULL, 969.7155, 374.4255, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (758, 'space_B043', 0, '粤AD00309', '2026-05-05 15:07:26.274929', 993.0155, 680.2005, '2026-05-05 15:07:26.276434', 'QR_SPACE_B043', '2026-04-19 05:34:49.770390', 969.7155, 641.0005, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (759, 'space_B044', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 629.0005000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B044', NULL, 969.7155, 589.8005, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (760, 'space_B045', 0, '沪AD82967', '2026-05-05 15:07:26.274929', 993.0155, 577.8105, '2026-05-05 15:07:26.276434', 'QR_SPACE_B045', '2026-04-19 05:34:49.770390', 969.7155, 538.6105, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (761, 'space_B046', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 792.5505, '2026-05-05 15:07:26.276434', 'QR_SPACE_B046', NULL, 969.7155, 753.3505, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (762, 'space_B047', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 741.3505, '2026-05-05 15:07:26.276434', 'QR_SPACE_B047', NULL, 969.7155, 702.1505, 'B1', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (763, 'space_B048', 0, NULL, '2026-05-05 15:07:26.274929', 513.3955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B048', NULL, 490.0955, 544.7725, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (764, 'space_B049', 0, NULL, '2026-05-05 15:07:26.274929', 564.5955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B049', NULL, 541.2955000000001, 544.7725, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (765, 'space_B050', 0, NULL, '2026-05-05 15:07:26.274929', 615.7955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B050', NULL, 592.4955, 544.7725, 'B1', 0, 0, '粤CGBBEE', 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (766, 'space_B051', 0, NULL, '2026-05-05 15:07:26.274929', 666.9955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B051', NULL, 643.6955, 544.7725, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (767, 'space_B052', 0, NULL, '2026-05-05 15:07:26.274929', 718.1954999999999, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B052', NULL, 694.8955, 544.7725, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (768, 'space_B053', 0, NULL, '2026-05-05 15:07:26.274929', 769.3855, 584.1415000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B053', NULL, 746.0855, 544.9415, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (769, 'space_B054', 0, NULL, '2026-05-05 15:07:26.274929', 196.2845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_B054', NULL, 172.9845, 625.9765, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (770, 'space_B055', 0, '沪B36066', '2026-05-05 15:07:26.274929', 247.48450000000003, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_B055', '2026-04-19 05:38:22.454534', 224.1845, 625.9765, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (771, 'space_B056', 0, NULL, '2026-05-05 15:07:26.274929', 298.6845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_B056', NULL, 275.3845, 625.9765, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (772, 'space_B057', 0, NULL, '2026-05-05 15:07:26.274929', 349.8845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_B057', NULL, 326.5845, 625.9765, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (773, 'space_B058', 0, NULL, '2026-05-05 15:07:26.274929', 401.0845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_B058', NULL, 377.7845, 625.9765, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (774, 'space_B059', 0, NULL, '2026-05-05 15:07:26.274929', 452.2745, 665.3455, '2026-05-05 15:07:26.276434', 'QR_SPACE_B059', NULL, 428.9745, 626.1455, 'B1', 0, 0, '粤C7Y7Q3', 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (775, 'space_B060', 0, NULL, '2026-05-05 15:07:26.274929', 513.3945, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B060', NULL, 490.09450000000004, 626.0615, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (776, 'space_B061', 0, NULL, '2026-05-05 15:07:26.274929', 564.5944999999999, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B061', NULL, 541.2945, 626.0615, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (777, 'space_B062', 1, NULL, '2026-05-05 15:07:26.274929', 615.7945, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B062', NULL, 592.4945, 626.0615, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (778, 'space_B063', 0, NULL, '2026-05-05 15:07:26.274929', 666.9944999999999, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B063', NULL, 643.6945, 626.0615, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (779, 'space_B064', 0, '沪B94232', '2026-05-05 15:07:26.274929', 718.1945, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_B064', '2026-04-19 05:38:22.454534', 694.8945, 626.0615, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (780, 'space_B065', 0, NULL, '2026-05-05 15:07:26.274929', 769.3845, 665.4305, '2026-05-05 15:07:26.276434', 'QR_SPACE_B065', NULL, 746.0845, 626.2305, 'B1', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (781, 'space_C001', 0, NULL, '2026-05-06 07:20:04.262923', 196.2835, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_C001', NULL, 172.9835, 287.5775, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (782, 'space_C002', 0, NULL, '2026-05-05 15:07:26.274929', 196.2835, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_C002', NULL, 172.9835, 370.1785, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (783, 'space_C003', 0, NULL, '2026-05-05 15:07:26.274929', 247.48250000000002, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_C003', NULL, 224.1825, 287.5775, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (784, 'space_C004', 0, '粤C81096', '2026-05-05 15:07:26.274929', 247.48250000000002, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_C004', '2026-04-19 05:38:22.454534', 224.1825, 370.1785, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (785, 'space_C005', 0, NULL, '2026-05-05 15:07:26.274929', 298.6825, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_C005', NULL, 275.3825, 287.5775, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (786, 'space_C006', 0, NULL, '2026-05-05 15:07:26.274929', 298.6825, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_C006', NULL, 275.3825, 370.1785, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (787, 'space_C007', 0, NULL, '2026-05-05 15:07:26.274929', 349.8815, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_C007', NULL, 326.5815, 287.5775, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (788, 'space_C008', 0, '京A15965', '2026-05-05 15:07:26.274929', 349.8815, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_C008', '2026-04-19 05:38:22.454534', 326.5815, 370.1785, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (789, 'space_C009', 0, NULL, '2026-05-05 15:07:26.274929', 401.08050000000003, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_C009', NULL, 377.7805, 287.5775, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (790, 'space_C010', 0, NULL, '2026-05-05 15:07:26.274929', 401.08050000000003, 409.3785, '2026-05-05 15:07:26.276434', 'QR_SPACE_C010', NULL, 377.7805, 370.1785, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (791, 'space_C011', 1, NULL, '2026-05-05 15:07:26.274929', 452.27950000000004, 326.7775, '2026-05-05 15:07:26.276434', 'QR_SPACE_C011', NULL, 428.97950000000003, 287.5775, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (792, 'space_C012', 0, '沪B27577', '2026-05-05 15:07:26.274929', 452.27950000000004, 409.5475, '2026-05-05 15:07:26.276434', 'QR_SPACE_C012', '2026-04-19 05:38:22.454534', 428.97950000000003, 370.3475, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (793, 'space_C013', 0, NULL, '2026-05-05 15:07:26.274929', 196.28650000000002, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C013', NULL, 172.9865, 544.4215, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (794, 'space_C014', 1, NULL, '2026-05-05 15:07:26.274929', 247.4865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C014', NULL, 224.1865, 544.4215, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (795, 'space_C015', 1, NULL, '2026-05-05 15:07:26.274929', 298.6865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C015', NULL, 275.3865, 544.4215, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (796, 'space_C016', 0, NULL, '2026-05-05 15:07:26.274929', 349.8865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C016', NULL, 326.5865, 544.4215, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (797, 'space_C017', 0, NULL, '2026-05-05 15:07:26.274929', 401.0865, 583.6215000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C017', NULL, 377.7865, 544.4215, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (798, 'space_C018', 0, NULL, '2026-05-05 15:07:26.274929', 452.2765, 583.7905000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C018', NULL, 428.9765, 544.5905, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (799, 'space_C019', 0, NULL, '2026-05-05 15:07:26.274929', 513.3955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_C019', NULL, 490.0955, 287.6625, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (800, 'space_C020', 1, NULL, '2026-05-05 15:07:26.274929', 513.3955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_C020', NULL, 490.0955, 370.2635, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (801, 'space_C021', 0, '粤C10457', '2026-05-05 15:07:26.274929', 564.5955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_C021', '2026-04-19 05:38:22.454534', 541.2955000000001, 287.6625, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (802, 'space_C022', 0, NULL, '2026-05-05 15:07:26.274929', 564.5955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_C022', NULL, 541.2955000000001, 370.2635, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (803, 'space_C023', 0, NULL, '2026-05-05 15:07:26.274929', 615.7955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_C023', NULL, 592.4955, 287.6625, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (804, 'space_C024', 0, NULL, '2026-05-05 15:07:26.274929', 615.7955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_C024', NULL, 592.4955, 370.2635, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (805, 'space_C025', 0, '粤C19172', '2026-05-05 15:07:26.274929', 666.9955, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_C025', '2026-04-19 05:38:22.454534', 643.6955, 287.6625, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (806, 'space_C026', 1, NULL, '2026-05-05 15:07:26.274929', 666.9955, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_C026', NULL, 643.6955, 370.2635, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (807, 'space_C027', 0, NULL, '2026-05-05 15:07:26.274929', 718.1954999999999, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_C027', NULL, 694.8955, 287.6625, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (808, 'space_C028', 0, NULL, '2026-05-05 15:07:26.274929', 718.1954999999999, 409.4635, '2026-05-05 15:07:26.276434', 'QR_SPACE_C028', NULL, 694.8955, 370.2635, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (809, 'space_C029', 0, NULL, '2026-05-05 15:07:26.274929', 769.3855, 326.8625, '2026-05-05 15:07:26.276434', 'QR_SPACE_C029', NULL, 746.0855, 287.6625, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (810, 'space_C030', 0, NULL, '2026-05-05 15:07:26.274929', 769.3855, 409.6325, '2026-05-05 15:07:26.276434', 'QR_SPACE_C030', NULL, 746.0855, 370.4325, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (811, 'space_C031', 0, NULL, '2026-05-05 15:07:26.274929', 237.9035, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_C031', NULL, 214.6035, 47.2992, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (812, 'space_C032', 0, NULL, '2026-05-05 15:07:26.274929', 289.1035, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_C032', NULL, 265.8035, 47.2992, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (813, 'space_C033', 0, NULL, '2026-05-05 15:07:26.274929', 340.30350000000004, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_C033', NULL, 317.00350000000003, 47.2992, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (814, 'space_C034', 0, NULL, '2026-05-05 15:07:26.274929', 391.50350000000003, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_C034', NULL, 368.2035, 47.2992, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (815, 'space_C035', 0, NULL, '2026-05-05 15:07:26.274929', 442.7035, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_C035', NULL, 419.4035, 47.2992, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (816, 'space_C036', 0, NULL, '2026-05-05 15:07:26.274929', 493.8935, 86.4992, '2026-05-05 15:07:26.276434', 'QR_SPACE_C036', NULL, 470.5935, 47.2992, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (817, 'space_C037', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 351.39549999999997, '2026-05-05 15:07:26.276434', 'QR_SPACE_C037', NULL, 969.7155, 312.1955, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (818, 'space_C038', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 300.1955, '2026-05-05 15:07:26.276434', 'QR_SPACE_C038', NULL, 969.7155, 260.9955, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (819, 'space_C039', 0, '粤AD61212', '2026-05-05 15:07:26.274929', 993.0155, 249.00549999999998, '2026-05-05 15:07:26.276434', 'QR_SPACE_C039', '2026-04-19 05:34:49.770390', 969.7155, 209.8055, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (820, 'space_C040', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 516.0155, '2026-05-05 15:07:26.276434', 'QR_SPACE_C040', NULL, 969.7155, 476.8155, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (821, 'space_C041', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 464.8155, '2026-05-05 15:07:26.276434', 'QR_SPACE_C041', NULL, 969.7155, 425.6155, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (822, 'space_C042', 0, '沪AD13707', '2026-05-05 15:07:26.274929', 993.0155, 413.6255, '2026-05-05 15:07:26.276434', 'QR_SPACE_C042', '2026-04-19 05:34:49.770390', 969.7155, 374.4255, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (823, 'space_C043', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 680.2005, '2026-05-05 15:07:26.276434', 'QR_SPACE_C043', NULL, 969.7155, 641.0005, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (824, 'space_C044', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 629.0005000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C044', NULL, 969.7155, 589.8005, '1F', 90, 1, '沪B72YQG', 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (825, 'space_C045', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 577.8105, '2026-05-05 15:07:26.276434', 'QR_SPACE_C045', NULL, 969.7155, 538.6105, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (826, 'space_C046', 0, '粤AD13985', '2026-05-05 15:07:26.274929', 993.0155, 792.5505, '2026-05-05 15:07:26.276434', 'QR_SPACE_C046', '2026-04-19 05:34:49.770390', 969.7155, 753.3505, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (827, 'space_C047', 0, NULL, '2026-05-05 15:07:26.274929', 993.0155, 741.3505, '2026-05-05 15:07:26.276434', 'QR_SPACE_C047', NULL, 969.7155, 702.1505, '1F', 90, 1, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (828, 'space_C048', 0, NULL, '2026-05-05 15:07:26.274929', 513.3955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C048', NULL, 490.0955, 544.7725, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (829, 'space_C049', 0, '粤C77014', '2026-05-05 15:07:26.274929', 564.5955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C049', '2026-04-19 05:38:22.454534', 541.2955000000001, 544.7725, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (830, 'space_C050', 0, NULL, '2026-05-05 15:07:26.274929', 615.7955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C050', NULL, 592.4955, 544.7725, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (831, 'space_C051', 0, NULL, '2026-05-05 15:07:26.274929', 666.9955, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C051', NULL, 643.6955, 544.7725, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (832, 'space_C052', 0, NULL, '2026-05-05 15:07:26.274929', 718.1954999999999, 583.9725000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C052', NULL, 694.8955, 544.7725, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (833, 'space_C053', 0, NULL, '2026-05-05 15:07:26.274929', 769.3855, 584.1415000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C053', NULL, 746.0855, 544.9415, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (834, 'space_C054', 0, NULL, '2026-05-05 15:07:26.274929', 196.2845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_C054', NULL, 172.9845, 625.9765, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (835, 'space_C055', 0, NULL, '2026-05-05 15:07:26.274929', 247.48450000000003, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_C055', NULL, 224.1845, 625.9765, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (836, 'space_C056', 0, NULL, '2026-05-05 15:07:26.274929', 298.6845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_C056', NULL, 275.3845, 625.9765, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (837, 'space_C057', 0, NULL, '2026-05-05 15:07:26.274929', 349.8845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_C057', NULL, 326.5845, 625.9765, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (838, 'space_C058', 0, NULL, '2026-05-05 15:07:26.274929', 401.0845, 665.1765, '2026-05-05 15:07:26.276434', 'QR_SPACE_C058', NULL, 377.7845, 625.9765, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (839, 'space_C059', 0, NULL, '2026-05-05 15:07:26.274929', 452.2745, 665.3455, '2026-05-05 15:07:26.276434', 'QR_SPACE_C059', NULL, 428.9745, 626.1455, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (840, 'space_C060', 0, '京A18277', '2026-05-05 15:07:26.274929', 513.3945, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C060', '2026-04-19 05:38:22.454534', 490.09450000000004, 626.0615, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (841, 'space_C061', 0, NULL, '2026-05-05 15:07:26.274929', 564.5944999999999, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C061', NULL, 541.2945, 626.0615, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (842, 'space_C062', 1, NULL, '2026-05-05 15:07:26.274929', 615.7945, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C062', NULL, 592.4945, 626.0615, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (843, 'space_C063', 0, NULL, '2026-05-05 15:07:26.274929', 666.9944999999999, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C063', NULL, 643.6945, 626.0615, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (844, 'space_C064', 0, NULL, '2026-05-05 15:07:26.274929', 718.1945, 665.2615000000001, '2026-05-05 15:07:26.276434', 'QR_SPACE_C064', NULL, 694.8945, 626.0615, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (845, 'space_C065', 0, NULL, '2026-05-05 15:07:26.274929', 769.3845, 665.4305, '2026-05-05 15:07:26.276434', 'QR_SPACE_C065', NULL, 746.0845, 626.2305, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (1187, 'space_TEST02', 0, NULL, '2026-05-06 10:04:40.996178', 100, 100, '2026-05-06 10:04:40.996178', 'SPOT-16DE046F656B4B93', NULL, 90, 90, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (1188, 'space_DBG01', 0, NULL, '2026-05-06 10:07:04.733725', 100, 100, '2026-05-06 10:07:04.733725', 'SPOT-5529288240724EC1', NULL, 90, 90, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (1189, 'space_NAV01', 0, NULL, '2026-05-06 10:29:26.577928', 100, 100, '2026-05-06 10:29:26.577928', 'SPOT-0FA075E40BBF4745', NULL, 90, 90, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (1190, 'space_NAV02', 0, NULL, '2026-05-06 10:29:26.581966', 200, 100, '2026-05-06 10:29:26.581966', 'SPOT-91B3B2CCDCC5434D', NULL, 190, 90, '1F', 0, 0, NULL, 'parking', '', NULL, NULL);
INSERT INTO `parking_space` VALUES (1205, 'LOC_1F_出入口', 0, NULL, '2026-05-06 13:29:29.539360', 100, 88, '2026-05-06 13:29:29.539360', 'LOC-D3A54BEA33944539', NULL, 48, 88, '1F', 0, 0, NULL, 'location', '出入口', NULL, NULL);
INSERT INTO `parking_space` VALUES (1206, 'LOC_B1_出入口', 0, NULL, '2026-05-06 13:29:29.539360', 100, 88, '2026-05-06 13:29:29.539360', 'LOC-A8AC1EA5A5D6437F', NULL, 48, 88, 'B1', 0, 0, NULL, 'location', '出入口', NULL, NULL);
INSERT INTO `parking_space` VALUES (1207, 'LOC_B2_出入口', 0, '浙ASB886', '2026-05-07 10:20:48.851247', 100, 88, '2026-05-06 13:29:29.539360', 'LOC-F1AD63EA930443DA', NULL, 48, 88, 'B2', 0, 0, NULL, 'location', '出入口', NULL, NULL);

-- ----------------------------
-- Table structure for sentinel_bank_card
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_bank_card`;
CREATE TABLE `sentinel_bank_card`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bank_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `card_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `holder_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `card_last4` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `bin_prefix` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `sentinel_bank_card_user_id_2d84bfa2_fk_sentinel_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_bank_card_user_id_2d84bfa2_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_bank_card
-- ----------------------------
INSERT INTO `sentinel_bank_card` VALUES (1, '中国工商银行', '借记卡', '李四', '9012', '622202', 1, 1, '2026-04-20 15:26:00.651800', '2026-04-20 15:26:00.651800', 2);

-- ----------------------------
-- Table structure for sentinel_device
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_device`;
CREATE TABLE `sentinel_device`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `device_type` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `serial_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `uptime` decimal(5, 2) NOT NULL,
  `last_maintenance` date NULL DEFAULT NULL,
  `fault_detail` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `offline_since` datetime(6) NULL DEFAULT NULL,
  `paper_level` int NULL DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `serial_number`(`serial_number` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_device
-- ----------------------------
INSERT INTO `sentinel_device` VALUES (10, '入口摄像头 1', 'camera', 'B2 层 - 入口', 'CAM-B2-IN-001', 'online', 99.85, '2026-04-20', '', NULL, NULL, '2026-05-05 14:41:26.331587', '2026-05-07 09:28:53.392956');
INSERT INTO `sentinel_device` VALUES (11, '出口摄像头 1', 'camera', 'B2 层 - 出口', 'CAM-B2-OUT-001', 'online', 99.92, '2026-04-18', '', NULL, NULL, '2026-05-05 14:41:26.331587', '2026-05-05 14:41:26.331587');
INSERT INTO `sentinel_device` VALUES (12, '入口摄像头 2', 'camera', 'B1 层 - 入口', 'CAM-B1-IN-002', 'online', 99.80, '2026-04-19', '', NULL, NULL, '2026-05-05 14:41:26.331587', '2026-05-07 09:28:54.722368');
INSERT INTO `sentinel_device` VALUES (13, '出口摄像头 2', 'camera', 'B1 层 - 出口', 'CAM-B1-OUT-002', 'online', 99.88, '2026-04-21', '', NULL, NULL, '2026-05-05 14:41:26.331587', '2026-05-05 14:41:26.331587');
INSERT INTO `sentinel_device` VALUES (14, '入口摄像头 3', 'camera', '1F 层 - 入口', 'CAM-1F-IN-003', 'online', 99.95, '2026-04-17', '', NULL, NULL, '2026-05-05 14:41:26.331587', '2026-05-05 14:41:26.331587');
INSERT INTO `sentinel_device` VALUES (15, '出口摄像头 3', 'camera', '1F 层 - 出口', 'CAM-1F-OUT-003', 'online', 99.78, '2026-04-22', '', NULL, NULL, '2026-05-05 14:41:26.331587', '2026-05-05 14:41:26.331587');

-- ----------------------------
-- Table structure for sentinel_parking_session
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_parking_session`;
CREATE TABLE `sentinel_parking_session`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `entry_time` datetime(6) NOT NULL,
  `exit_time` datetime(6) NULL DEFAULT NULL,
  `amount` decimal(10, 2) NOT NULL,
  `payment_status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `vehicle_id` bigint NOT NULL,
  `spot_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `sentinel_parking_ses_vehicle_id_d216c216_fk_sentinel_`(`vehicle_id` ASC) USING BTREE,
  INDEX `sentinel_parking_session_spot_id_a67fb204_fk_parking_space_id`(`spot_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_parking_ses_vehicle_id_d216c216_fk_sentinel_` FOREIGN KEY (`vehicle_id`) REFERENCES `sentinel_vehicle` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sentinel_parking_session_spot_id_a67fb204_fk_parking_space_id` FOREIGN KEY (`spot_id`) REFERENCES `parking_space` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 59 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_parking_session
-- ----------------------------
INSERT INTO `sentinel_parking_session` VALUES (4, '2026-04-14 16:03:44.461508', NULL, 0.00, 'pending', '2026-04-14 16:03:44.461508', 4, NULL);
INSERT INTO `sentinel_parking_session` VALUES (5, '2026-04-14 16:09:53.487549', NULL, 0.00, 'pending', '2026-04-14 16:09:53.489098', 5, NULL);
INSERT INTO `sentinel_parking_session` VALUES (6, '2026-04-14 16:14:20.039752', NULL, 0.00, 'pending', '2026-04-14 16:14:20.041842', 6, NULL);
INSERT INTO `sentinel_parking_session` VALUES (7, '2026-04-15 15:05:16.524368', NULL, 0.00, 'pending', '2026-04-15 15:05:16.524888', 7, NULL);
INSERT INTO `sentinel_parking_session` VALUES (8, '2026-04-15 15:35:42.634407', NULL, 0.00, 'pending', '2026-04-15 15:35:42.634407', 8, NULL);
INSERT INTO `sentinel_parking_session` VALUES (9, '2026-04-15 15:49:08.747032', NULL, 0.00, 'pending', '2026-04-15 15:49:08.747032', 9, NULL);
INSERT INTO `sentinel_parking_session` VALUES (10, '2026-04-15 16:05:18.941981', NULL, 0.00, 'pending', '2026-04-15 16:05:18.941981', 10, NULL);
INSERT INTO `sentinel_parking_session` VALUES (11, '2026-04-15 16:05:20.378773', NULL, 0.00, 'pending', '2026-04-15 16:05:20.378773', 11, NULL);
INSERT INTO `sentinel_parking_session` VALUES (12, '2026-04-15 16:19:11.182853', NULL, 0.00, 'pending', '2026-04-15 16:19:11.182853', 12, NULL);
INSERT INTO `sentinel_parking_session` VALUES (13, '2026-04-15 16:19:12.527844', NULL, 0.00, 'pending', '2026-04-15 16:19:12.527844', 13, NULL);
INSERT INTO `sentinel_parking_session` VALUES (14, '2026-04-15 16:22:27.861493', NULL, 0.00, 'pending', '2026-04-15 16:22:27.861493', 14, NULL);
INSERT INTO `sentinel_parking_session` VALUES (15, '2026-04-15 16:31:26.038769', NULL, 0.00, 'pending', '2026-04-15 16:31:26.038769', 15, NULL);
INSERT INTO `sentinel_parking_session` VALUES (16, '2026-04-15 16:31:26.977030', NULL, 0.00, 'pending', '2026-04-15 16:31:26.977030', 16, NULL);
INSERT INTO `sentinel_parking_session` VALUES (17, '2026-04-18 15:25:27.926491', NULL, 0.00, 'pending', '2026-04-18 15:25:27.927506', 17, NULL);
INSERT INTO `sentinel_parking_session` VALUES (18, '2026-04-18 15:26:24.809393', NULL, 0.00, 'pending', '2026-04-18 15:26:24.809393', 18, NULL);
INSERT INTO `sentinel_parking_session` VALUES (19, '2026-04-19 13:38:22.454534', '2026-04-20 06:21:35.395193', 85.00, 'paid', '2026-04-20 06:16:36.071162', 21, NULL);
INSERT INTO `sentinel_parking_session` VALUES (20, '2026-04-19 13:38:22.454534', '2026-04-20 06:29:03.917550', 85.00, 'paid', '2026-04-20 06:23:38.928556', 22, NULL);
INSERT INTO `sentinel_parking_session` VALUES (24, '2026-05-06 08:45:27.085755', NULL, 0.00, 'paid', '2026-05-06 08:45:27.086754', 26, 683);
INSERT INTO `sentinel_parking_session` VALUES (30, '2026-05-07 09:37:39.599402', NULL, 0.00, 'paid', '2026-05-07 09:37:39.600406', 32, 543);
INSERT INTO `sentinel_parking_session` VALUES (31, '2026-05-07 09:38:07.466953', NULL, 0.00, 'paid', '2026-05-07 09:38:07.468468', 33, 551);
INSERT INTO `sentinel_parking_session` VALUES (32, '2026-05-07 10:20:26.374953', NULL, 0.00, 'pending', '2026-05-07 10:20:26.374953', 5, 540);
INSERT INTO `sentinel_parking_session` VALUES (33, '2026-05-07 10:20:26.455372', NULL, 0.00, 'pending', '2026-05-07 10:20:26.456372', 17, 573);
INSERT INTO `sentinel_parking_session` VALUES (34, '2026-05-07 10:20:26.515217', NULL, 0.00, 'pending', '2026-05-07 10:20:26.516218', 9, 692);
INSERT INTO `sentinel_parking_session` VALUES (35, '2026-05-07 10:20:26.577059', NULL, 0.00, 'paid', '2026-05-07 10:20:26.577059', 34, 546);
INSERT INTO `sentinel_parking_session` VALUES (36, '2026-05-07 10:20:26.635453', NULL, 0.00, 'paid', '2026-05-07 10:20:26.635453', 35, 569);
INSERT INTO `sentinel_parking_session` VALUES (37, '2026-05-07 10:20:26.694787', NULL, 0.00, 'paid', '2026-05-07 10:20:26.694787', 36, 554);
INSERT INTO `sentinel_parking_session` VALUES (38, '2026-05-07 10:20:26.755633', NULL, 0.00, 'paid', '2026-05-07 10:20:26.756633', 26, 553);
INSERT INTO `sentinel_parking_session` VALUES (39, '2026-05-07 10:20:26.810556', NULL, 0.00, 'paid', '2026-05-07 10:20:26.811556', 32, 685);
INSERT INTO `sentinel_parking_session` VALUES (40, '2026-05-07 10:20:26.868865', NULL, 0.00, 'paid', '2026-05-07 10:20:26.868865', 33, 568);
INSERT INTO `sentinel_parking_session` VALUES (41, '2026-05-07 10:20:46.374059', NULL, 0.00, 'pending', '2026-05-07 10:20:46.375056', 5, 574);
INSERT INTO `sentinel_parking_session` VALUES (42, '2026-05-07 10:20:46.428323', NULL, 0.00, 'pending', '2026-05-07 10:20:46.428323', 17, 521);
INSERT INTO `sentinel_parking_session` VALUES (43, '2026-05-07 10:20:46.480877', NULL, 0.00, 'pending', '2026-05-07 10:20:46.480877', 9, 563);
INSERT INTO `sentinel_parking_session` VALUES (44, '2026-05-07 10:20:46.535872', NULL, 0.00, 'paid', '2026-05-07 10:20:46.535872', 34, 528);
INSERT INTO `sentinel_parking_session` VALUES (45, '2026-05-07 10:20:46.587999', NULL, 0.00, 'paid', '2026-05-07 10:20:46.587999', 35, 561);
INSERT INTO `sentinel_parking_session` VALUES (46, '2026-05-07 10:20:46.640608', NULL, 0.00, 'paid', '2026-05-07 10:20:46.641610', 36, 558);
INSERT INTO `sentinel_parking_session` VALUES (47, '2026-05-07 10:20:46.698973', NULL, 0.00, 'paid', '2026-05-07 10:20:46.698973', 26, 549);
INSERT INTO `sentinel_parking_session` VALUES (48, '2026-05-07 10:20:46.757674', NULL, 0.00, 'paid', '2026-05-07 10:20:46.757674', 32, 690);
INSERT INTO `sentinel_parking_session` VALUES (49, '2026-05-07 10:20:46.806157', NULL, 0.00, 'paid', '2026-05-07 10:20:46.806157', 33, 557);
INSERT INTO `sentinel_parking_session` VALUES (50, '2026-05-07 10:20:48.402686', NULL, 0.00, 'pending', '2026-05-07 10:20:48.403700', 5, 523);
INSERT INTO `sentinel_parking_session` VALUES (51, '2026-05-07 10:20:48.457877', NULL, 0.00, 'pending', '2026-05-07 10:20:48.457877', 17, 552);
INSERT INTO `sentinel_parking_session` VALUES (52, '2026-05-07 10:20:48.508636', NULL, 0.00, 'pending', '2026-05-07 10:20:48.508636', 9, 691);
INSERT INTO `sentinel_parking_session` VALUES (53, '2026-05-07 10:20:48.570883', NULL, 0.00, 'paid', '2026-05-07 10:20:48.571882', 34, 542);
INSERT INTO `sentinel_parking_session` VALUES (54, '2026-05-07 10:20:48.625272', NULL, 0.00, 'paid', '2026-05-07 10:20:48.625272', 35, 688);
INSERT INTO `sentinel_parking_session` VALUES (55, '2026-05-07 10:20:48.684290', NULL, 0.00, 'paid', '2026-05-07 10:20:48.684290', 36, 566);
INSERT INTO `sentinel_parking_session` VALUES (56, '2026-05-07 10:20:48.740536', NULL, 0.00, 'paid', '2026-05-07 10:20:48.741535', 26, 684);
INSERT INTO `sentinel_parking_session` VALUES (57, '2026-05-07 10:20:48.799234', NULL, 0.00, 'paid', '2026-05-07 10:20:48.799234', 32, 570);
INSERT INTO `sentinel_parking_session` VALUES (58, '2026-05-07 10:20:48.848231', NULL, 0.00, 'paid', '2026-05-07 10:20:48.848231', 33, 1207);

-- ----------------------------
-- Table structure for sentinel_payment
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_payment`;
CREATE TABLE `sentinel_payment`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `transaction_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `amount` decimal(10, 2) NOT NULL,
  `method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `remark` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `session_id` bigint NULL DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `biz_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `transaction_id`(`transaction_id` ASC) USING BTREE,
  INDEX `sentinel_payment_session_id_fcee567c_fk_sentinel_`(`session_id` ASC) USING BTREE,
  INDEX `sentinel_payment_user_id_b3d0f682_fk_sentinel_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_payment_session_id_fcee567c_fk_sentinel_` FOREIGN KEY (`session_id`) REFERENCES `sentinel_parking_session` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sentinel_payment_user_id_b3d0f682_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 29 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_payment
-- ----------------------------
INSERT INTO `sentinel_payment` VALUES (1, 'PAY_8_1776613246605', 18.80, 'balance', 'success', '余额支付', '2026-04-19 15:40:46.605930', NULL, 8, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (2, 'PAY_8_1776613282553', 18.80, 'balance', 'success', '余额支付', '2026-04-19 15:41:22.553371', NULL, 8, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (3, 'PAYSBX_9_1776613519598', 12.30, 'alipay', 'success', '停车费支付', '2026-04-19 15:45:19.613251', NULL, 9, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (6, 'PAY_2_1776658295084', 120.00, 'balance', 'refunded', '预约车位费用 | 退款:预约创建失败自动补偿', '2026-04-20 04:11:35.084737', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (7, 'PAY_2_1776658391463', 120.00, 'balance', 'refunded', '预约车位费用 | 退款:预约创建失败自动补偿', '2026-04-20 04:13:11.464050', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (8, 'PAY_2_1776658462592', 120.00, 'balance', 'success', '预约车位费用', '2026-04-20 04:14:22.592991', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (9, 'PAY_2_1776659004229', 60.00, 'balance', 'refunded', '预约车位费用 | 退款:预约创建失败自动补偿', '2026-04-20 04:23:24.230402', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (10, 'PAY_2_1776659161614', 60.00, 'balance', 'success', '预约车位费用', '2026-04-20 04:26:01.614653', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (11, 'QPAY_1776662775860', 18.50, 'wechat', 'success', '匿名快速缴费|车牌:京A12345', '2026-04-20 05:26:15.860618', NULL, 12, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (12, 'QPAY_1776663167812', 190.00, 'wechat', 'success', '匿名快速缴费|车牌:浙F77777', '2026-04-20 05:32:47.814065', 18, 1, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (13, 'QPAY_1776666095384', 85.00, 'wechat', 'success', '匿名快速缴费|车牌:60730', '2026-04-20 06:21:35.384853', 19, 12, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (14, 'QPAY_1776666239073', 85.00, 'wechat', 'success', '匿名快速缴费|车牌:粤C36090', '2026-04-20 06:23:59.073912', 20, 12, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (15, 'PAY_2_1776666622135', 120.00, 'balance', 'success', '预约车位费用', '2026-04-20 06:30:22.135541', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (16, 'PAY_2_1776667271071', 150.00, 'balance', 'success', '预约车位费用', '2026-04-20 06:41:11.071860', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (17, 'PAY_2_1776670596464', 1199.00, 'balance', 'success', '订阅套餐购买:尊享年卡套餐', '2026-04-20 07:36:36.464566', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (18, 'PAY_2_1777994275897', 90.00, 'balance', 'success', '预约车位费用', '2026-05-05 15:17:55.897832', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (19, 'PAY_2_1778052051900', 90.00, 'balance', 'refunded', '预约车位费用 | 退款:预约创建失败自动补偿', '2026-05-06 07:20:51.902804', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (20, 'PAY_2_1778052055506', 90.00, 'balance', 'refunded', '预约车位费用 | 退款:预约创建失败自动补偿', '2026-05-06 07:20:55.507194', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (21, 'QUICK_1778081506247', 2090.00, 'wechat', 'success', '快速缴费（按车牌）京A10001', '2026-05-06 15:31:46.248319', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (22, 'QUICK_1778081510573', 2090.00, 'card', 'success', '快速缴费（按车牌）京A10001', '2026-05-06 15:31:50.576083', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (23, 'QUICK_1778082081266', 2095.00, 'wechat', 'success', '快速缴费（按车牌）京A10001', '2026-05-06 15:41:21.268427', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (24, 'QUICK_1778083740389', 2095.00, 'alipay', 'success', '快速缴费（按车牌）京A10001', '2026-05-06 16:09:00.392785', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (25, 'QUICK_1778084345334', 2095.00, 'card', 'success', '快速缴费（按车牌）京A10001', '2026-05-06 16:19:05.335107', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (26, 'QUICK_1778084374197', 2095.00, 'card', 'success', '快速缴费（按车牌）京A10002', '2026-05-06 16:19:34.200139', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (27, 'QUICK_1778129301653', 2160.00, 'card', 'success', '快速缴费（按车牌）京A10008', '2026-05-07 04:48:21.658836', NULL, 2, 'parking_fee');
INSERT INTO `sentinel_payment` VALUES (28, 'QUICK_1778148401493', 562.00, 'balance', 'success', '快速缴费（余额）京A10003', '2026-05-07 10:06:41.501687', NULL, 2, 'parking_fee');

-- ----------------------------
-- Table structure for sentinel_pricing_rule
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_pricing_rule`;
CREATE TABLE `sentinel_pricing_rule`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rate_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `value` decimal(10, 2) NOT NULL,
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `effective_date` date NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `rate_type`(`rate_type` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_pricing_rule
-- ----------------------------
INSERT INTO `sentinel_pricing_rule` VALUES (1, 'hourly_standard', 5.00, '元/小时', '', 1, '2026-04-13', '2026-04-13 04:34:27.838113', '2026-04-13 04:34:27.838113');
INSERT INTO `sentinel_pricing_rule` VALUES (2, 'hourly_peak', 10.00, '元/小时', '', 1, '2026-04-13', '2026-04-13 04:34:27.841010', '2026-04-13 04:34:27.841010');
INSERT INTO `sentinel_pricing_rule` VALUES (3, 'grace_entry', 15.00, '分钟', '', 1, '2026-04-13', '2026-04-13 04:34:27.843124', '2026-04-13 04:34:27.843124');
INSERT INTO `sentinel_pricing_rule` VALUES (7, 'reservation_ev_surcharge', 10.00, '元/单', '预约充电桩附加费', 1, '2026-04-19', '2026-04-19 17:11:39.278272', '2026-04-19 17:11:39.278272');
INSERT INTO `sentinel_pricing_rule` VALUES (11, 'reservation_daily', 30.00, '元/天', '', 1, '2026-05-06', '2026-05-06 10:04:41.014265', '2026-05-06 10:04:41.014265');
INSERT INTO `sentinel_pricing_rule` VALUES (12, 'hourly_first', 6.00, '元/小时', '停车首小时收费', 1, '2026-05-07', '2026-05-07 09:51:45.875634', '2026-05-07 09:51:45.875634');
INSERT INTO `sentinel_pricing_rule` VALUES (13, 'hourly_subsequent', 4.00, '元/小时', '首小时后每小时收费', 1, '2026-05-07', '2026-05-07 09:51:45.878217', '2026-05-07 09:51:45.878217');
INSERT INTO `sentinel_pricing_rule` VALUES (14, 'hourly_switch_hour', 5.00, '小时', '超过此小时数切换为日租计费', 1, '2026-05-07', '2026-05-07 09:51:45.878217', '2026-05-07 09:51:45.878217');
INSERT INTO `sentinel_pricing_rule` VALUES (15, 'daily_rate', 30.00, '元/天', '超过5小时后的日租价格', 1, '2026-05-07', '2026-05-07 09:51:45.878217', '2026-05-07 09:51:45.878217');
INSERT INTO `sentinel_pricing_rule` VALUES (16, 'daily_cap', 60.00, '元/天', '每日最高收费限额', 1, '2026-05-07', '2026-05-07 09:51:45.878217', '2026-05-07 09:51:45.878217');

-- ----------------------------
-- Table structure for sentinel_recognition_record
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_recognition_record`;
CREATE TABLE `sentinel_recognition_record`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `scene` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `result_data` json NOT NULL,
  `plate_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `vehicle_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `action_taken` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `image_source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 97 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_recognition_record
-- ----------------------------
INSERT INTO `sentinel_recognition_record` VALUES (1, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'cv2\'', '2026-04-14 14:05:08.941677', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (2, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'cv2\'', '2026-04-14 14:05:32.800043', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (3, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'cv2\'', '2026-04-14 14:08:16.730075', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (4, 'entry', '{}', NULL, NULL, '识别过程出错: name \'cv2\' is not defined', '2026-04-14 14:47:58.749507', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (5, 'entry', '{\"detections\": []}', NULL, NULL, '未检测到车辆信息', '2026-04-14 15:14:39.211300', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (6, 'entry', '{\"detections\": []}', NULL, NULL, '未检测到车辆信息', '2026-04-14 15:37:30.041331', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (7, 'entry', '{\"detections\": []}', NULL, NULL, '未检测到车辆信息', '2026-04-14 15:49:51.967793', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (8, 'entry', '{\"detections\": []}', NULL, NULL, '未检测到车辆信息', '2026-04-14 15:57:53.964313', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (9, 'entry', '{\"detections\": [{\"bbox\": [0, 0, 660, 504], \"type\": \"vehicle (cropped)\", \"plate\": \"鲁325DE\", \"confidence\": 0.5}]}', '鲁325DE', 'vehicle (cropped)', '识别出入场车辆 鲁325DE，已自动分配车位 1F-A01-01 并开启计费。', '2026-04-14 16:03:28.147139', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (10, 'entry', '{\"detections\": [{\"bbox\": [0, 0, 660, 504], \"type\": \"vehicle (cropped)\", \"plate\": \"鲁B325DE\", \"confidence\": 0.5}]}', '鲁B325DE', 'vehicle (cropped)', '识别出入场车辆 鲁B325DE，已自动分配车位 1F-A01-03 并开启计费。', '2026-04-14 16:09:36.737930', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (11, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"鲁CRA6B00\", \"confidence\": 0.79}]}', '鲁CRA6B00', 'car', '识别出入场车辆 鲁CRA6B00，已自动分配车位 1F-A01-04 并开启计费。', '2026-04-14 16:14:18.807266', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (12, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"鲁CRA6B00\", \"confidence\": 0.79}]}', '鲁CRA6B00', 'car', '车辆 鲁CRA6B00 已经在场内，跳过登记。', '2026-04-14 16:14:26.253228', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (13, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"鲁CRA6B00\", \"confidence\": 0.79}]}', '鲁CRA6B00', 'car', '车辆 鲁CRA6B00 已经在场内，跳过登记。', '2026-04-14 16:18:23.099726', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (14, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"鲁CRA6B00\", \"confidence\": 0.79}]}', '鲁CRA6B00', 'car', '车辆 鲁CRA6B00 已经在场内，跳过登记。', '2026-04-15 14:52:19.782362', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (15, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.79}]}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 14:59:47.741798', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (16, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.79}]}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 15:02:55.821542', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (17, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙GB00001\", \"confidence\": 0.79}]}', '浙GB00001', 'car', '识别出入场车辆 浙GB00001，已自动分配车位 1F-A01-06 并开启计费。', '2026-04-15 15:04:59.223002', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (18, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\"}]}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 15:16:50.134981', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (19, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\"}]}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 15:18:46.716318', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (20, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.79, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\"}]}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 15:27:02.293698', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (21, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.79, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\"}]}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 15:29:00.317879', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (22, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙GB00001\", \"confidence\": 0.79, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\"}]}', '浙GB00001', 'car', '车辆 浙GB00001 已经在场内，跳过登记。', '2026-04-15 15:32:59.363108', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (23, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙GB0000\", \"confidence\": 0.79, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\"}]}', '浙GB0000', 'car', '识别出入场车辆 浙GB0000，已自动分配车位 1F-A01-08 并开启计费。', '2026-04-15 15:35:25.319445', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (24, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙G00001\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}]}', '浙G00001', 'car', '识别出入场车辆 浙G00001，已自动分配车位 1F-A01-09 并开启计费。', '2026-04-15 15:48:51.204795', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (25, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:04:57.741921', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (26, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙877777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙877777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙877777\", \"vehicle_type\": \"car\"}}', '浙877777', 'car', '识别出入场车辆 浙877777，已自动分配车位 1F-A01-11 并开启计费。', '2026-04-15 16:05:17.176194', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (27, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"浙305201\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙305201\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙305201\", \"vehicle_type\": \"car\"}}', '浙305201', 'car', '识别出入场车辆 浙305201，已自动分配车位 1F-A02-01 并开启计费。', '2026-04-15 16:05:18.956696', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (28, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙G00001\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\", \"vehicle_type\": \"car\"}}', '浙G00001', 'car', '车辆 浙G00001 已经在场内，跳过登记。', '2026-04-15 16:05:20.394387', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (29, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:13:37.228649', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (30, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙877777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙877777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙877777\", \"vehicle_type\": \"car\"}}', '浙877777', 'car', '车辆 浙877777 已经在场内，跳过登记。', '2026-04-15 16:13:56.619635', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (31, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"浙305201\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙305201\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙305201\", \"vehicle_type\": \"car\"}}', '浙305201', 'car', '车辆 浙305201 已经在场内，跳过登记。', '2026-04-15 16:13:58.361678', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (32, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙G00001\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\", \"vehicle_type\": \"car\"}}', '浙G00001', 'car', '车辆 浙G00001 已经在场内，跳过登记。', '2026-04-15 16:13:59.736479', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (33, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:16:52.028123', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (34, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙877777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙877777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙877777\", \"vehicle_type\": \"car\"}}', '浙877777', 'car', '车辆 浙877777 已经在场内，跳过登记。', '2026-04-15 16:17:10.726883', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (35, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"浙305201\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙305201\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙305201\", \"vehicle_type\": \"car\"}}', '浙305201', 'car', '车辆 浙305201 已经在场内，跳过登记。', '2026-04-15 16:17:11.744477', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (36, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙G00001\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\", \"vehicle_type\": \"car\"}}', '浙G00001', 'car', '车辆 浙G00001 已经在场内，跳过登记。', '2026-04-15 16:17:12.527482', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (37, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:18:50.463596', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (38, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙B77777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙B77777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙B77777\", \"vehicle_type\": \"car\"}}', '浙B77777', 'car', '识别出入场车辆 浙B77777，已自动分配车位 1F-A02-04 并开启计费。', '2026-04-15 16:19:09.485408', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (39, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"浙E05201\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙E05201\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙E05201\", \"vehicle_type\": \"car\"}}', '浙E05201', 'car', '识别出入场车辆 浙E05201，已自动分配车位 1F-A02-06 并开启计费。', '2026-04-15 16:19:11.196576', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (40, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙G00001\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\", \"vehicle_type\": \"car\"}}', '浙G00001', 'car', '车辆 浙G00001 已经在场内，跳过登记。', '2026-04-15 16:19:12.542556', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (41, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:22:04.863932', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (42, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 16:22:23.799990', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (43, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 16:22:25.671365', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (44, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"G00001T\", \"confidence\": 0.79, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"G00001T\"}], \"main_result\": {\"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"G00001T\", \"vehicle_type\": \"car\"}}', 'G00001T', 'car', '识别出入场车辆 G00001T，已自动分配车位 1F-A02-07 并开启计费。', '2026-04-15 16:22:26.818097', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (45, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:22:37.221665', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (46, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 16:22:39.559406', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (47, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 16:22:40.811550', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (48, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"G00001T\", \"confidence\": 0.79, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"G00001T\"}], \"main_result\": {\"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"G00001T\", \"vehicle_type\": \"car\"}}', 'G00001T', 'car', '车辆 G00001T 已经在场内，跳过登记。', '2026-04-15 16:22:41.511571', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (49, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:28:49.660684', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (50, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 16:29:05.217252', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (51, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 16:29:06.213564', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (52, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 16:29:06.992055', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (53, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:31:11.457863', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (54, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙AET8777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙AET8777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙AET8777\", \"vehicle_type\": \"car\"}}', '浙AET8777', 'car', '识别出入场车辆 浙AET8777，已自动分配车位 1F-A02-08 并开启计费。', '2026-04-15 16:31:24.991260', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (55, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"浙U305201\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙U305201\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙U305201\", \"vehicle_type\": \"car\"}}', '浙U305201', 'car', '识别出入场车辆 浙U305201，已自动分配车位 1F-A02-11 并开启计费。', '2026-04-15 16:31:26.048587', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (56, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙G00001\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\", \"vehicle_type\": \"car\"}}', '浙G00001', 'car', '车辆 浙G00001 已经在场内，跳过登记。', '2026-04-15 16:31:26.987841', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (57, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 16:41:25.970493', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (58, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙AET8777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙AET8777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙AET8777\", \"vehicle_type\": \"car\"}}', '浙AET8777', 'car', '车辆 浙AET8777 已经在场内，跳过登记。', '2026-04-15 16:41:42.651178', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (59, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"浙U305201\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙U305201\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙U305201\", \"vehicle_type\": \"car\"}}', '浙U305201', 'car', '车辆 浙U305201 已经在场内，跳过登记。', '2026-04-15 16:41:44.365888', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (60, 'entry', '{\"detections\": [{\"bbox\": [0.19, 0.61, 367.42, 176.74], \"type\": \"car\", \"plate\": \"浙G00001\", \"confidence\": 0.79, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\", \"vehicle_type\": \"car\"}}', '浙G00001', 'car', '车辆 浙G00001 已经在场内，跳过登记。', '2026-04-15 16:41:45.704081', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (61, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"浙U305201\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙U305201\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙U305201\", \"vehicle_type\": \"car\"}}', '浙U305201', 'car', '车辆 浙U305201 已经在场内，跳过登记。', '2026-04-15 16:42:17.606050', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (62, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'paddleocr\'', '2026-04-15 16:49:25.465110', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (63, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'paddleocr\'', '2026-04-15 16:50:39.322223', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (64, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'paddleocr\'', '2026-04-15 17:00:59.328897', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (65, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'paddleocr\'', '2026-04-15 17:06:10.796531', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (66, 'entry', '{}', NULL, NULL, '识别过程出错: No module named \'paddleocr\'', '2026-04-15 17:06:15.771074', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (67, 'entry', '{}', NULL, NULL, '识别过程出错: Unknown argument: use_gpu', '2026-04-15 17:11:12.370797', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (68, 'entry', '{}', NULL, NULL, '识别过程出错: Unknown argument: show_log', '2026-04-15 17:13:14.527076', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (69, 'entry', '{}', NULL, NULL, '识别过程出错: Unknown argument: show_log', '2026-04-15 17:15:21.978385', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (70, 'entry', '{}', NULL, NULL, '识别过程出错: PaddleOCR.predict() got an unexpected keyword argument \'cls\'', '2026-04-15 17:20:52.770446', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (71, 'entry', '{}', NULL, NULL, NULL, '2026-04-15 17:26:16.639771', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (72, 'entry', '{}', NULL, NULL, '识别过程出错: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]  (at ..\\paddle\\fluid\\framework\\new_executor\\instruction\\onednn\\onednn_instruction.cc:118)\n', '2026-04-15 17:29:12.299813', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (73, 'entry', '{}', NULL, NULL, '识别过程出错: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]  (at ..\\paddle\\fluid\\framework\\new_executor\\instruction\\onednn\\onednn_instruction.cc:118)\n', '2026-04-15 17:30:54.822339', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (74, 'entry', '{}', NULL, NULL, '识别过程出错: Unknown argument: use_gpu', '2026-04-15 17:32:23.655500', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (75, 'entry', '{}', NULL, NULL, '识别过程出错: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]  (at ..\\paddle\\fluid\\framework\\new_executor\\instruction\\onednn\\onednn_instruction.cc:118)\n', '2026-04-15 17:33:48.414359', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (76, 'entry', '{}', NULL, NULL, '识别过程出错: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]  (at ..\\paddle\\fluid\\framework\\new_executor\\instruction\\onednn\\onednn_instruction.cc:118)\n', '2026-04-15 17:35:57.446382', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (77, 'entry', '{}', NULL, NULL, '识别过程出错: too many values to unpack (expected 3)', '2026-04-15 17:38:42.463971', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (78, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 17:39:58.824934', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (79, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 17:42:26.083816', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (80, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-15 17:44:14.670951', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (81, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-18 15:07:56.811120', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (82, 'entry', '{}', NULL, NULL, '识别过程出错: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()', '2026-04-18 15:11:14.099367', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (83, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-18 15:12:55.088716', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (84, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-18 15:15:05.782099', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (85, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-18 15:18:53.085026', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (86, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"\", \"confidence\": 0.96, \"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\"}], \"main_result\": {\"energy_type\": \"Standard\", \"plate_color\": \"Unknown\", \"plate_number\": \"\", \"vehicle_type\": \"car\"}}', '', 'car', '检测到车辆但未识别出车牌，无法自动入场。', '2026-04-18 15:21:45.759908', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (87, 'entry', '{\"detections\": [{\"bbox\": [64.75, 7.52, 363.86, 223.65], \"type\": \"car\", \"plate\": \"苏D3Q520\", \"confidence\": 0.96, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\", \"vehicle_type\": \"car\"}}', '苏D3Q520', 'car', '识别入场车辆 苏D3Q520，已自动分配车位 1F-A02-12 并开启计费。', '2026-04-18 15:25:09.612181', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (88, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙F77777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\", \"vehicle_type\": \"car\"}}', '浙F77777', 'car', '识别入场车辆 浙F77777，已自动分配车位 B1-A01-02 并开启计费。', '2026-04-18 15:25:44.567290', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (89, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙F77777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\", \"vehicle_type\": \"car\"}}', '浙F77777', 'car', '车辆 浙F77777 已经在场内，跳过登记。', '2026-04-18 15:29:48.044848', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (90, 'entry', '{\"detections\": [{\"bbox\": [0.52, 0.74, 473.66, 340.83], \"type\": \"car\", \"plate\": \"浙F77777\", \"confidence\": 0.83, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\", \"vehicle_type\": \"car\"}}', '浙F77777', 'car', '车辆 浙F77777 已经在场内，跳过登记。', '2026-04-18 15:31:39.702305', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (91, 'entry', '{\"detections\": [{\"bbox\": [64.15, 2.97, 361.53, 229.68], \"type\": \"car\", \"plate\": \"苏D3Q520\", \"confidence\": 0.76, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\", \"vehicle_type\": \"car\"}}', '苏D3Q520', 'car', '车辆 苏D3Q520 已经在场内，跳过登记。', '2026-04-18 15:54:08.785954', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (92, 'entry', '{\"detections\": [{\"bbox\": [64.15, 2.97, 361.53, 229.68], \"type\": \"car\", \"plate\": \"苏D3Q520\", \"confidence\": 0.76, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\", \"vehicle_type\": \"car\"}}', '苏D3Q520', 'car', '车辆 苏D3Q520 已经在场内，跳过登记。', '2026-04-18 15:57:29.262476', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (93, 'entry', '{\"detections\": [{\"bbox\": [0, 0, 660, 504], \"type\": \"vehicle (cropped)\", \"plate\": \"鲁B325DE\", \"confidence\": 0.5, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"鲁B325DE\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"鲁B325DE\", \"vehicle_type\": \"vehicle (cropped)\"}}', '鲁B325DE', 'vehicle (cropped)', '车辆 鲁B325DE 已经在场内，跳过登记。', '2026-04-18 15:57:44.199027', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (94, 'entry', '{\"detections\": [{\"bbox\": [0.45, 3.89, 469.09, 341.44], \"type\": \"car\", \"plate\": \"浙F77777\", \"confidence\": 0.41, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙F77777\", \"vehicle_type\": \"car\"}}', '浙F77777', 'car', '车辆 浙F77777 已经在场内，跳过登记。', '2026-04-18 15:57:56.519364', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (95, 'entry', '{\"detections\": [{\"bbox\": [64.15, 2.97, 361.53, 229.68], \"type\": \"car\", \"plate\": \"苏D3Q520\", \"confidence\": 0.76, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"苏D3Q520\", \"vehicle_type\": \"car\"}}', '苏D3Q520', 'car', '车辆 苏D3Q520 已经在场内，跳过登记。', '2026-04-18 15:58:03.735673', NULL);
INSERT INTO `sentinel_recognition_record` VALUES (96, 'entry', '{\"detections\": [{\"bbox\": [0, 0, 369, 182], \"type\": \"vehicle (cropped)\", \"plate\": \"浙G00001\", \"confidence\": 0.5, \"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\"}], \"main_result\": {\"energy_type\": \"ICE\", \"plate_color\": \"Blue\", \"plate_number\": \"浙G00001\", \"vehicle_type\": \"vehicle (cropped)\"}}', '浙G00001', 'vehicle (cropped)', '车辆 浙G00001 已经在场内，跳过登记。', '2026-04-18 15:58:08.043638', NULL);

-- ----------------------------
-- Table structure for sentinel_reservation
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_reservation`;
CREATE TABLE `sentinel_reservation`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `start_time` time(6) NOT NULL,
  `end_time` time(6) NOT NULL,
  `total_amount` decimal(10, 2) NOT NULL,
  `booking_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `qr_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `spot_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `end_date` date NULL DEFAULT NULL,
  `payment_method` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `payment_transaction_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `booking_code`(`booking_code` ASC) USING BTREE,
  INDEX `sentinel_reservation_user_id_1ef6890f_fk_sentinel_user_id`(`user_id` ASC) USING BTREE,
  INDEX `sentinel_reservation_spot_id_1026ed0c_fk_parking_space_id`(`spot_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_reservation_spot_id_1026ed0c_fk_parking_space_id` FOREIGN KEY (`spot_id`) REFERENCES `parking_space` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sentinel_reservation_user_id_1ef6890f_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_reservation
-- ----------------------------
INSERT INTO `sentinel_reservation` VALUES (5, '2026-05-06', '08:00:00.000000', '12:00:00.000000', 90.00, 'SENT-6CEF16', '', 'cancelled', '2026-05-05 15:17:55.931534', '2026-05-05 15:17:55.931534', 781, 2, '2026-05-08', 'balance', '');

-- ----------------------------
-- Table structure for sentinel_spot_connection
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_spot_connection`;
CREATE TABLE `sentinel_spot_connection`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `distance` double NOT NULL,
  `from_spot_id` bigint NOT NULL,
  `to_spot_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `sentinel_spot_connection_from_spot_id_to_spot_id_67a80757_uniq`(`from_spot_id` ASC, `to_spot_id` ASC) USING BTREE,
  INDEX `sentinel_sp_from_sp_42ff6a_idx`(`from_spot_id` ASC, `to_spot_id` ASC) USING BTREE,
  INDEX `sentinel_spot_connection_to_spot_id_7c4466a8_fk_parking_space_id`(`to_spot_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_spot_connec_from_spot_id_63ccada9_fk_parking_s` FOREIGN KEY (`from_spot_id`) REFERENCES `parking_space` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sentinel_spot_connection_to_spot_id_7c4466a8_fk_parking_space_id` FOREIGN KEY (`to_spot_id`) REFERENCES `parking_space` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1084 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_spot_connection
-- ----------------------------
INSERT INTO `sentinel_spot_connection` VALUES (1083, 5, 1189, 1190);

-- ----------------------------
-- Table structure for sentinel_subscription
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_subscription`;
CREATE TABLE `sentinel_subscription`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `plan` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `price` decimal(10, 2) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  `plan_ref_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `sentinel_subscription_user_id_aa859c1d_fk_sentinel_user_id`(`user_id` ASC) USING BTREE,
  INDEX `sentinel_subscriptio_plan_ref_id_c23dd513_fk_sentinel_`(`plan_ref_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_subscriptio_plan_ref_id_c23dd513_fk_sentinel_` FOREIGN KEY (`plan_ref_id`) REFERENCES `sentinel_subscription_plan` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sentinel_subscription_user_id_aa859c1d_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_subscription
-- ----------------------------
INSERT INTO `sentinel_subscription` VALUES (1, 'monthly', 149.00, '2026-04-20', '2026-05-20', 0, '2026-04-20 07:32:40.096848', 2, 1);
INSERT INTO `sentinel_subscription` VALUES (2, 'yearly', 1199.00, '2026-04-20', '2027-04-20', 1, '2026-04-20 07:36:36.510896', 2, 3);
INSERT INTO `sentinel_subscription` VALUES (3, 'monthly', 149.00, '2026-05-01', '2026-05-11', 1, '2026-05-06 10:04:41.006645', 14, NULL);
INSERT INTO `sentinel_subscription` VALUES (4, 'monthly', 149.00, '2026-05-01', '2026-05-11', 1, '2026-05-06 10:07:04.739909', 15, NULL);

-- ----------------------------
-- Table structure for sentinel_subscription_plan
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_subscription_plan`;
CREATE TABLE `sentinel_subscription_plan`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `price` decimal(10, 2) NOT NULL,
  `duration_days` int UNSIGNED NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `sort_order` int UNSIGNED NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_recommended` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `code`(`code` ASC) USING BTREE,
  CONSTRAINT `sentinel_subscription_plan_chk_1` CHECK (`duration_days` >= 0),
  CONSTRAINT `sentinel_subscription_plan_chk_2` CHECK (`sort_order` >= 0)
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_subscription_plan
-- ----------------------------
INSERT INTO `sentinel_subscription_plan` VALUES (1, 'monthly', '尊享月卡套餐', 149.00, 30, '适合高频通勤，按月计费，灵活续费', 1, 10, '2026-04-19 16:09:16.754103', '2026-04-19 16:09:16.754103', 1);
INSERT INTO `sentinel_subscription_plan` VALUES (2, 'quarterly', '尊享季卡套餐', 399.00, 90, '季卡优惠，兼顾价格与周期', 1, 20, '2026-04-19 16:09:16.756673', '2026-04-19 16:09:16.756673', 0);
INSERT INTO `sentinel_subscription_plan` VALUES (3, 'yearly', '尊享年卡套餐', 1199.00, 365, '全年优惠价格，适合长期固定停车用户', 1, 30, '2026-04-19 16:09:16.758331', '2026-04-19 16:09:16.758331', 0);

-- ----------------------------
-- Table structure for sentinel_topup_record
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_topup_record`;
CREATE TABLE `sentinel_topup_record`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `transaction_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `amount` decimal(10, 2) NOT NULL,
  `payment_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `remark` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `transaction_id`(`transaction_id` ASC) USING BTREE,
  INDEX `sentinel_topup_record_user_id_536846ea_fk_sentinel_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_topup_record_user_id_536846ea_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_topup_record
-- ----------------------------
INSERT INTO `sentinel_topup_record` VALUES (1, 'TOPUP_8_1776613246591', 88.80, 'wechat', 'success', '', '2026-04-19 15:40:46.591316', 8);
INSERT INTO `sentinel_topup_record` VALUES (2, 'TOPUP_8_1776613282538', 88.80, 'wechat', 'success', '', '2026-04-19 15:41:22.538752', 8);
INSERT INTO `sentinel_topup_record` VALUES (3, 'TOPUP_2_1776613354846', 1000.00, 'wechat', 'success', '', '2026-04-19 15:42:34.846480', 2);
INSERT INTO `sentinel_topup_record` VALUES (4, 'TOPUP_9_1776613519598', 66.60, 'wechat', 'success', '', '2026-04-19 15:45:19.598372', 9);
INSERT INTO `sentinel_topup_record` VALUES (5, 'TOPUP_2_1776614025363', 1000.00, 'wechat', 'success', '', '2026-04-19 15:53:45.364182', 2);
INSERT INTO `sentinel_topup_record` VALUES (6, 'TOPUP_2_1776671145652', 1000.00, 'wechat', 'success', '', '2026-04-20 07:45:45.652764', 2);
INSERT INTO `sentinel_topup_record` VALUES (7, 'TOPUP_2_1778081181826', 50.00, 'wechat', 'success', '', '2026-05-06 15:26:21.827318', 2);

-- ----------------------------
-- Table structure for sentinel_user
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_user`;
CREATE TABLE `sentinel_user`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `last_login` datetime(6) NULL DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `first_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `last_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `avatar` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `is_vip` tinyint(1) NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `totp_secret` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `two_factor_enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `phone`(`phone` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_user
-- ----------------------------
INSERT INTO `sentinel_user` VALUES (1, 'pbkdf2_sha256$1200000$kNd7VRKysZAg1SnioNjWgp$MBGnQaoX5VTw2lGh3BRzc76vQfqvamoNwQx5AS05Dtc=', '2026-04-20 16:06:55.204462', 1, 'admin', '', '', 'admin@sentinel.com', 1, 1, '2026-04-12 18:42:33.512479', '13800000000', '', 0, 'active', 'S5EZVXUEQRSETPAT3AWRMNZBZV4KEJRK', 0);
INSERT INTO `sentinel_user` VALUES (2, 'pbkdf2_sha256$1200000$tgE42zSmqrX4a0wPzfpvzM$J4FgexJKkiu+l6hjNSJm1bf1uHCvx8p51Yw9/7Y5Yr0=', NULL, 0, 'lisi', '', '', '', 0, 1, '2026-04-13 03:43:19.751956', '17633669683', 'avatars/1663065890848637.jpg', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (3, 'pbkdf2_sha256$1200000$cSZ2oGl82n6kYoPEcSCCkJ$fwZMeBckdBfH9iCFVJJ+1zTziEaM4fayCtZRC8c2aWc=', NULL, 0, 'user', '', '', '', 0, 1, '2026-04-13 04:34:27.846644', '13800000001', '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (4, 'pbkdf2_sha256$1200000$UPhqkrF1IkKvR7Spl45qdh$TM+HBedl8XcRcJ08n988sDnZcSWJvikDh9vsvdkn21U=', NULL, 0, 'user2', '', '', '', 0, 1, '2026-04-13 04:34:28.314455', '13800000002', '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (5, 'pbkdf2_sha256$1200000$VtWm4vkZ3dYvLB9XGIsKZK$W2AzR5bInMtK4pChBb/mdQZk2JTTyIeCx1qxf2PSdRg=', NULL, 0, 'user3', '', '', '', 0, 1, '2026-04-13 04:34:28.782387', '13800000003', '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (7, 'pbkdf2_sha256$1200000$HpHdcTBqnSEKLifyEalhel$vqQHjWGR4pIdbIVEHq5VniQS/xMqq74gl2SeGQmAdnw=', NULL, 0, 'testuser', '', '', 'test@example.com', 0, 1, '2026-04-19 05:32:57.691769', NULL, '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (8, 'pbkdf2_sha256$1200000$J86gKhdnosngkNxgsegpQZ$1uUo7jMY0HBMjZzOXFnlR78/se0U7yXxnTWJgYZKqLI=', NULL, 0, 'smoke_user', '', '', 'smoke_user@example.com', 0, 1, '2026-04-19 15:40:46.118466', NULL, '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (9, 'pbkdf2_sha256$1200000$tUNHVWqtJPYNajKTurq2Wu$R/MQXngKX6LrS/HqVOkCoRD/JjOOSq05kuEtMuhqTRo=', NULL, 0, 'smoke_api_user', '', '', 'smoke_api_user@example.com', 0, 1, '2026-04-19 15:45:19.083343', NULL, '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (12, '!ewHRlnMvdURVu6PuUE1H9X4BVZz488m58Pgp2W4x', NULL, 0, 'guest_quickpay', '', '', 'guest_quickpay@sentinel.local', 0, 1, '2026-04-20 05:26:15.854058', NULL, '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (13, '', '2026-04-20 13:15:26.268229', 1, 'admin_test_cli', '', '', 'admin_test_cli@example.com', 1, 1, '2026-04-20 13:15:26.236992', NULL, '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (14, 'pbkdf2_sha256$1200000$rO88of4qaZYLmnk4JmUUcu$dkf75lDnNZrQXQn9pHF3LmvJU3hyGCaTbzSrfOvB2rw=', NULL, 0, 'test_sub2', '', '', '', 0, 1, '2026-05-06 10:04:40.504729', '13999999998', '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (15, 'pbkdf2_sha256$1200000$iuID91An2QjH0z3zcbV8Du$gxNwBhPiP1zMcE9duoXgnvUxdLmJ3Lcjm6/xwfBtETQ=', NULL, 0, 'debug_sub', '', '', '', 0, 1, '2026-05-06 10:07:04.230566', '13999999997', '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (16, 'pbkdf2_sha256$1200000$LKmyCRfGoNaoxhzSqVJprz$3grRS4jkRU8DMHrtd3ajSnZ9Q0bWsKR2+NPMAZEhcdQ=', NULL, 1, 'nav_test', '', '', '', 1, 1, '2026-05-06 10:29:26.074179', '13900000001', '', 0, 'active', NULL, 0);
INSERT INTO `sentinel_user` VALUES (17, 'pbkdf2_sha256$1200000$y1j7KbJiNGAYun9bESte3k$ykvOjC/hc8WDGzzR9yg06PxulcWeg0u0ECm0ApU2sWg=', NULL, 1, 'nav_test2', '', '', '', 1, 1, '2026-05-06 10:29:40.988526', '13900000002', '', 0, 'active', NULL, 0);

-- ----------------------------
-- Table structure for sentinel_user_balance
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_user_balance`;
CREATE TABLE `sentinel_user_balance`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `balance` decimal(10, 2) NOT NULL,
  `total_recharged` decimal(10, 2) NOT NULL,
  `total_consumed` decimal(10, 2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_user_balance_user_id_ad2e7d9b_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_user_balance
-- ----------------------------
INSERT INTO `sentinel_user_balance` VALUES (1, 140.00, 177.60, 37.60, '2026-04-19 15:40:46.597704', '2026-04-19 15:41:22.557277', 8);
INSERT INTO `sentinel_user_balance` VALUES (2, 749.00, 3050.00, 2301.00, '2026-04-19 15:42:31.413813', '2026-05-07 10:06:41.506176', 2);
INSERT INTO `sentinel_user_balance` VALUES (3, 66.60, 66.60, 0.00, '2026-04-19 15:45:19.598372', '2026-04-19 15:45:19.598372', 9);
INSERT INTO `sentinel_user_balance` VALUES (6, 0.00, 0.00, 0.00, '2026-04-20 04:49:23.311200', '2026-04-20 04:49:23.311200', 7);

-- ----------------------------
-- Table structure for sentinel_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_user_groups`;
CREATE TABLE `sentinel_user_groups`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `sentinel_user_groups_user_id_group_id_7390dc48_uniq`(`user_id` ASC, `group_id` ASC) USING BTREE,
  INDEX `sentinel_user_groups_group_id_e8e8e4e6_fk_auth_group_id`(`group_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_user_groups_group_id_e8e8e4e6_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sentinel_user_groups_user_id_21ac440d_fk_sentinel_user_id` FOREIGN KEY (`user_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_user_groups
-- ----------------------------

-- ----------------------------
-- Table structure for sentinel_vehicle
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_vehicle`;
CREATE TABLE `sentinel_vehicle`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `plate_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `brand` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `model` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `color` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `owner_id` bigint NOT NULL,
  `is_simulated` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `plate_number`(`plate_number` ASC) USING BTREE,
  INDEX `sentinel_vehicle_owner_id_5baa22be_fk_sentinel_user_id`(`owner_id` ASC) USING BTREE,
  CONSTRAINT `sentinel_vehicle_owner_id_5baa22be_fk_sentinel_user_id` FOREIGN KEY (`owner_id`) REFERENCES `sentinel_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sentinel_vehicle
-- ----------------------------
INSERT INTO `sentinel_vehicle` VALUES (1, '沪A·88801', 'Tesla', 'Model 3', '', 0, '2026-04-13 04:34:28.312128', '2026-04-13 04:34:28.312128', 3, 0);
INSERT INTO `sentinel_vehicle` VALUES (2, '沪A·88802', 'Tesla', 'Model 3', '', 0, '2026-04-13 04:34:28.777777', '2026-04-13 04:34:28.777777', 4, 0);
INSERT INTO `sentinel_vehicle` VALUES (3, '沪A·88803', 'Tesla', 'Model 3', '', 0, '2026-04-13 04:34:29.249267', '2026-04-13 04:34:29.249267', 5, 0);
INSERT INTO `sentinel_vehicle` VALUES (4, '鲁325DE', '未知品牌', '识别录入', '', 0, '2026-04-14 16:03:44.449048', '2026-04-14 16:03:44.449048', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (5, '鲁B325DE', '未知品牌', '识别录入', '', 0, '2026-04-14 16:09:53.286603', '2026-04-14 16:09:53.286603', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (6, '鲁CRA6B00', '未知品牌', '识别录入', '', 0, '2026-04-14 16:14:20.034617', '2026-04-14 16:14:20.034617', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (7, '浙GB00001', '未知品牌', '识别录入', '', 0, '2026-04-15 15:05:16.513238', '2026-04-15 15:05:16.513238', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (8, '浙GB0000', '未知品牌', '识别录入', '', 0, '2026-04-15 15:35:42.611614', '2026-04-15 15:35:42.611614', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (9, '浙G00001', '未知品牌', '识别录入', '', 0, '2026-04-15 15:49:08.726866', '2026-04-15 15:49:08.726866', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (10, '浙877777', '未知品牌', '识别录入', '', 0, '2026-04-15 16:05:18.921413', '2026-04-15 16:05:18.921413', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (11, '浙305201', '未知品牌', '识别录入', '', 0, '2026-04-15 16:05:20.372050', '2026-04-15 16:05:20.372050', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (12, '浙B77777', '未知品牌', '识别录入', '', 0, '2026-04-15 16:19:11.160185', '2026-04-15 16:19:11.160185', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (13, '浙E05201', '未知品牌', '识别录入', '', 0, '2026-04-15 16:19:12.507093', '2026-04-15 16:19:12.507093', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (14, 'G00001T', '未知品牌', '识别录入', '', 0, '2026-04-15 16:22:27.854433', '2026-04-15 16:22:27.854433', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (15, '浙AET8777', '未知品牌', '识别录入', '', 0, '2026-04-15 16:31:26.019586', '2026-04-15 16:31:26.019586', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (16, '浙U305201', '未知品牌', '识别录入', '', 0, '2026-04-15 16:31:26.959687', '2026-04-15 16:31:26.959687', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (17, '苏D3Q520', '未知品牌', '识别录入', '', 0, '2026-04-18 15:25:27.916577', '2026-04-18 15:25:27.916577', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (18, '浙F77777', '未知品牌', '识别录入', '', 0, '2026-04-18 15:26:24.802873', '2026-04-18 15:26:24.802873', 1, 0);
INSERT INTO `sentinel_vehicle` VALUES (20, '豫R8JU93', '燃油车', '蓝牌燃油', '未知', 1, '2026-04-19 11:07:46.886474', '2026-04-19 11:07:46.886474', 2, 0);
INSERT INTO `sentinel_vehicle` VALUES (21, '粤C60730', '临时车辆', '', '', 0, '2026-04-20 06:16:36.071162', '2026-04-20 06:16:36.071162', 12, 0);
INSERT INTO `sentinel_vehicle` VALUES (22, '粤C36090', '临时车辆', '', '', 0, '2026-04-20 06:23:38.913311', '2026-04-20 06:23:38.913311', 12, 0);
INSERT INTO `sentinel_vehicle` VALUES (26, '新AD1ILO', '模拟车辆', '自动创建', '', 0, '2026-05-06 08:45:27.075935', '2026-05-06 08:45:27.075935', 2, 1);
INSERT INTO `sentinel_vehicle` VALUES (32, '苏AGN567', '模拟车辆', '自动创建', '', 0, '2026-05-07 09:37:39.590406', '2026-05-07 09:37:39.590406', 2, 1);
INSERT INTO `sentinel_vehicle` VALUES (33, '浙ASB886', '模拟车辆', '自动创建', '', 0, '2026-05-07 09:38:07.452270', '2026-05-07 09:38:07.452270', 2, 1);
INSERT INTO `sentinel_vehicle` VALUES (34, '浙A28001', '模拟车辆', '自动创建', '', 0, '2026-05-07 10:20:26.572059', '2026-05-07 10:20:26.572059', 2, 1);
INSERT INTO `sentinel_vehicle` VALUES (35, '粤R8888R', '模拟车辆', '自动创建', '', 0, '2026-05-07 10:20:26.628774', '2026-05-07 10:20:26.628774', 2, 1);
INSERT INTO `sentinel_vehicle` VALUES (36, '川A42344', '模拟车辆', '自动创建', '', 0, '2026-05-07 10:20:26.690787', '2026-05-07 10:20:26.690787', 2, 1);

SET FOREIGN_KEY_CHECKS = 1;
