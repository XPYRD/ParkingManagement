/**
 * 测试地图数据流
 * 验证前端是否能正确获取和处理停车位数据
 */

const API_BASE = 'http://localhost:8000/api/v1'

async function testDataFlow() {
  console.log('═════════════════════════════════════════')
  console.log('🧪 停车场地图数据流测试')
  console.log('═════════════════════════════════════════\n')

  try {
    // 1. 测试 SVG API
    console.log('1️⃣  测试 SVG API...')
    const svgRes = await fetch(`${API_BASE}/parking/map/svg/`)
    const svgData = await svgRes.json()
    console.log(`   ✅ SVG API 返回:`, {
      code: svgData.code,
      width: svgData.data?.width,
      height: svgData.data?.height,
      svgLength: svgData.data?.svg?.length
    })

    // 2. 测试停车位 API
    console.log('\n2️⃣  测试停车位 API (B2 楼层)...')
    const spotsRes = await fetch(`${API_BASE}/parking/map/spaces/?floor=B2`)
    const spotsData = await spotsRes.json()
    console.log(`   ✅ 停车位 API 返回:`, {
      code: spotsData.code,
      floor: spotsData.floor,
      count: spotsData.count,
      firstSpot: spotsData.data?.[0]
    })

    // 3. 验证坐标数据
    if (spotsData.data && spotsData.data.length > 0) {
      console.log('\n3️⃣  坐标数据验证...')
      const firstSpot = spotsData.data[0]
      console.log(`   第一个停车位: ${firstSpot.space_id}`)
      console.log(`   - x: ${firstSpot.x}`)
      console.log(`   - y: ${firstSpot.y}`)
      console.log(`   - center_x: ${firstSpot.center_x}`)
      console.log(`   - center_y: ${firstSpot.center_y}`)
      console.log(`   - floor: ${firstSpot.floor}`)
      console.log(`   - status: ${firstSpot.status}`)
      
      // 4. 验证过滤逻辑
      console.log('\n4️⃣  数据过滤验证...')
      const processedSpots = spotsData.data.map(space => ({
        id: space.space_id,
        spot_id: space.space_id,
        space_id: space.space_id,
        floor: space.floor,
        status: space.status,
        current_plate: space.current_plate,
        center_x: space.center_x,
        center_y: space.center_y,
        x: space.x,
        y: space.y
      }))
      
      console.log(`   ✅ 处理后的第一个停车位:`, processedSpots[0])
      
      // 5. 验证楼层过滤
      console.log('\n5️⃣  楼层过滤验证...')
      const selectedFloor = 'B2'
      const filteredSpots = processedSpots.filter(spot => spot.floor === selectedFloor)
      console.log(`   楼层 ${selectedFloor} 过滤结果: ${filteredSpots.length} 个停车位`)
      
      if (filteredSpots.length === 0) {
        console.log('   ⚠️  警告: 没有停车位通过楼层过滤！')
      } else {
        console.log(`   ✅ 成功获取 ${filteredSpots.length} 个停车位`)
      }
    }

    console.log('\n═════════════════════════════════════════')
    console.log('✅ 数据流测试完成！')
    console.log('═════════════════════════════════════════')
  } catch (err) {
    console.error('❌ 测试失败:', err)
  }
}

// 运行测试
testDataFlow()
