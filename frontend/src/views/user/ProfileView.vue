<template>
  <!-- 个人中心 -->
  <div class="px-4 md:px-8 max-w-7xl mx-auto py-8">
    <header class="mb-8">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">个人中心</h1>
      <p class="text-secondary text-sm mt-2">管理您的个人资料、车辆信息和系统偏好设置。</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- 左侧：个人资料 & 偏好设置 -->
      <div class="lg:col-span-4 space-y-6">
        
        <!-- 用户身份卡片 -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/20 relative overflow-hidden text-center">
           <div class="absolute top-0 left-0 w-full h-24 bg-gradient-to-br from-primary/20 to-transparent"></div>
           <div class="relative z-10 flex flex-col items-center">
              <el-avatar :size="80" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" class="border-4 border-surface shadow-md mb-4" />
              <h2 class="text-xl font-bold text-on-surface">{{ profile.username || 'User' }}</h2>
              
              <div v-if="profile.vip_level && profile.vip_level !== 'none'" class="mt-4 inline-flex items-center gap-1 bg-amber-50 text-amber-700 px-3 py-1 rounded-full text-xs font-bold border border-amber-200">
                 <span class="material-symbols-outlined text-sm">workspace_premium</span>
                 尊享 VIP
              </div>
           </div>
        </div>

        <!-- 基本设置 -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/20">
          <h3 class="text-sm font-bold text-on-surface uppercase tracking-widest mb-4">基本信息</h3>
          <el-form label-position="top" class="space-y-4">
            <el-form-item label="手机号码">
              <el-input v-model="profile.phone" size="large" readonly>
                 <template #append>
                    <el-button link type="primary">修改</el-button>
                 </template>
              </el-input>
            </el-form-item>
            <el-form-item label="常用邮箱">
              <el-input v-model="profile.email" size="large" />
            </el-form-item>
            <el-button type="primary" class="!w-full !mt-2" :loading="savingProfile" @click="handleSaveProfile">保存修改</el-button>
          </el-form>
        </div>

        <!-- 偏好设置 -->
        <div class="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/20">
          <h3 class="text-sm font-bold text-on-surface uppercase tracking-widest mb-4">偏好设置</h3>
          <div class="space-y-4">
             <div class="flex items-center justify-between">
                <div>
                   <p class="text-sm font-bold text-on-surface">短信通知</p>
                   <p class="text-xs text-secondary mt-0.5">接收车辆停放、费用等重要通知</p>
                </div>
                <el-switch v-model="prefs.sms" />
             </div>
             <el-divider class="!my-0" />
             <div class="flex items-center justify-between">
                <div>
                   <p class="text-sm font-bold text-on-surface">无感支付</p>
                   <p class="text-xs text-secondary mt-0.5">出场时自动扣除停车费</p>
                </div>
                <el-switch v-model="prefs.autoPay" />
             </div>
             <el-divider class="!my-0" />
             <div>
               <p class="text-sm font-bold text-on-surface">默认支付方式</p>
               <p class="text-xs text-secondary mt-0.5 mb-2">用于首页快速缴费、预约支付、停车费支付的默认选项</p>
               <el-select v-model="prefs.defaultPaymentMethod" class="w-full" @change="handleChangeDefaultPaymentMethod">
                <el-option label="余额支付" value="balance" />
                <el-option label="微信支付" value="wechat" />
                <el-option label="支付宝" value="alipay" />
                <el-option label="银行卡支付" value="card" :disabled="!hasBankCard" />
               </el-select>
               <p v-if="!hasBankCard" class="text-xs text-slate-500 mt-1">未添加银行卡时不可设为默认银行卡支付。</p>
             </div>
          </div>
        </div>

      </div>

      <!-- 右侧：车辆管理 & 预订记录 -->
      <div class="lg:col-span-8 space-y-8">
         
         <!-- 车辆管理 -->
        <section>
          <div class="flex justify-between items-center mb-6">
            <div>
               <h2 class="text-xl font-bold text-on-surface">我的车辆</h2>
               <p class="text-xs text-secondary mt-1">您最多可以绑定 3 辆车</p>
            </div>
            <el-button type="primary" plain class="!rounded-full hover:!shadow-md transition-shadow" @click="showAddCarDialog">
               <span class="material-symbols-outlined text-sm mr-1">add</span>
               添加车辆
            </el-button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div v-for="car in vehicles" :key="car.id" 
                  class="bg-surface-container-lowest rounded-2xl p-6 relative overflow-hidden transition-all group"
                  :class="car.is_primary ? 'border-2 border-primary shadow-sm hover:shadow-md' : 'border border-outline-variant/20 border-dashed hover:bg-surface-container-low'">
                
                <div v-if="car.is_primary" class="absolute top-0 right-0 bg-primary text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl">
                   首选车辆
                </div>
                
                <div class="flex items-start justify-between mb-6" :class="!car.is_primary && 'opacity-80 group-hover:opacity-100'">
                   <div class="flex gap-4 items-center">
                      <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="car.is_primary ? 'bg-primary/10' : 'bg-surface-container-high'">
                         <span class="material-symbols-outlined text-2xl" :class="car.is_primary ? 'text-primary' : 'text-secondary'">directions_car</span>
                      </div>
                      <div>
                         <p class="text-xs text-secondary uppercase tracking-wider mb-1" v-if="car.is_primary">默认车辆</p>
                         <h3 class="text-2xl font-black font-headline tracking-tighter text-on-surface">{{ car.plate_number }}</h3>
                      </div>
                   </div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-sm text-secondary border-t border-outline-variant/20 pt-4 mb-4">
                   <span>类型：{{ car.vehicle_type === 'car' ? '小型车' : (car.vehicle_type === 'suv' ? 'SUV' : '其他') }}</span>
                   <span>挂牌：{{ car.color || '未知' }}</span>
                </div>
                <div class="flex gap-2" :class="!car.is_primary && 'opacity-0 group-hover:opacity-100 md:opacity-100 transition-opacity'">
                   <el-button size="small" v-if="!car.is_primary" @click="handleSetPrimary(car.id)">设为默认</el-button>
                   <el-button size="small" type="primary" plain class="!flex-1" @click="showEditCarDialog(car)">编辑信息</el-button>
                   <el-button size="small" type="danger" plain @click="handleDeleteCar(car.id)">解绑</el-button>
                </div>
             </div>
             
             <div v-if="vehicles.length === 0" class="col-span-1 md:col-span-2 text-center p-8 bg-surface-container-lowest border border-dashed rounded-2xl text-secondary">
               暂无绑定的车辆
             </div>
          </div>
        </section>

        <!-- 预订记录 -->
        <section>
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-on-surface">最近预订</h2>
            <el-button link type="primary" v-if="reservations.length > 0">查看全部</el-button>
          </div>
          
          <div class="space-y-4" v-loading="loadingRes">
             <div v-for="res in reservations" :key="res.id" class="bg-surface-container-lowest rounded-xl p-4 border border-outline-variant/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div class="flex items-center gap-4">
                   <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="res.status === 'pending' ? 'bg-amber-50 text-amber-600' : 'bg-surface-container-high text-secondary'">
                      <span class="material-symbols-outlined">{{ res.status === 'pending' ? 'pending_actions' : 'check_circle' }}</span>
                   </div>
                   <div>
                      <p class="font-bold text-on-surface text-sm">{{ res.spot_detail ? `${res.spot_detail.floor}层 - ${res.spot_detail.zone}区 - ${res.spot_detail.spot_id}` : '未分配车位' }}</p>
                      <p class="text-xs text-secondary mt-0.5">{{ res.date }} {{ res.start_time.substring(0,5) }} - {{ res.end_time.substring(0,5) }}</p>
                   </div>
                </div>
                <div class="flex items-center justify-between md:justify-end gap-6 w-full md:w-auto">
                   <span class="font-bold text-sm" :class="res.status === 'pending' ? 'text-amber-600' : 'text-secondary'">
                     {{ res.status === 'pending' ? '即将开始' : (res.status === 'active' ? '进行中' : (res.status === 'completed' ? '已完成' : '已取消')) }}
                   </span>
                   <el-button v-if="res.status === 'pending'" size="small" plain type="danger" @click="handleCancelRes(res.id)">取消</el-button>
                   <el-button v-else size="small" plain>再订一次</el-button>
                </div>
             </div>
             
             <div v-if="reservations.length === 0" class="text-center p-8 bg-surface-container-lowest border rounded-2xl text-secondary">
               暂无预订记录
             </div>
          </div>
        </section>

      </div>
    </div>
    <!-- 添加车辆弹窗 -->
    <el-dialog v-model="addCarDialogVisible" title="添加车辆" width="500px" destroy-on-close @close="resetAddCarDialog">
      <el-form :model="carForm" ref="carFormRef" label-position="top">
        <el-form-item label="能源类型" prop="energy_type" :rules="[{ required: true, message: '请选择能源类型' }]">
          <el-select v-model="carForm.energy_type" placeholder="请选择" class="w-full">
            <el-option label="🔋 新能源车（绿牌）" value="new_energy" />
            <el-option label="⛽ 油车（蓝牌）" value="ice" />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 车牌号虚拟键盘 -->
      <div v-if="carForm.energy_type" class="mt-6 pt-6 border-t border-outline-variant/20">
        <PlateNumberInput 
          v-model="carForm.plate_number"
          :energy-type="carForm.energy_type"
          @complete="handlePlateComplete"
        />
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addCarDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="savingCar" 
            :disabled="!carForm.plate_number || (carForm.energy_type === 'new_energy' ? carForm.plate_number.length < 8 : carForm.plate_number.length < 7)"
            @click="submitAddCar"
          >
            添加车辆
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑车辆弹窗 -->
    <el-dialog v-model="editCarDialogVisible" title="编辑车辆" width="500px" destroy-on-close>
      <el-form :model="editCarForm" ref="editCarFormRef" label-position="top">
        <el-form-item label="车牌号" prop="plate_number" :rules="[{ required: true, message: '请输入车牌号' }]">
          <el-input 
            v-model="editCarForm.plate_number" 
            placeholder="例如：京A88888"
            readonly
            class="cursor-not-allowed"
          />
          <div class="text-xs text-secondary mt-2">车牌号不可修改，如需修改请解绑后重新添加</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editCarDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProfile, updateProfile, getVehicles, deleteVehicle, setPrimaryVehicle, addVehicle } from '@/api/user'
import { getReservations, cancelReservation } from '@/api/parking'
import PlateNumberInput from '@/components/PlateNumberInput.vue'
import { hasBoundBankCard } from '@/utils/bankCard'
import { getDefaultPaymentMethod, setDefaultPaymentMethod } from '@/utils/paymentPreference'

const profile = ref({})
const vehicles = ref([])
const reservations = ref([])
const savingProfile = ref(false)
const loadingRes = ref(false)
const hasBankCard = ref(false)

const addCarDialogVisible = ref(false)
const savingCar = ref(false)
const carFormRef = ref(null)
const carForm = reactive({
  plate_number: '',
  energy_type: '' // 'new_energy' | 'ice'
})

const editCarDialogVisible = ref(false)
const editCarFormRef = ref(null)
const editCarForm = reactive({
  plate_number: ''
})

const prefs = reactive({
  sms: true,
  autoPay: true,
  defaultPaymentMethod: 'wechat'
})

onMounted(() => {
  hasBankCard.value = hasBoundBankCard()
  const storedMethod = getDefaultPaymentMethod('wechat')
  prefs.defaultPaymentMethod = (!hasBankCard.value && storedMethod === 'card') ? 'wechat' : storedMethod
  loadData()
})

function handleChangeDefaultPaymentMethod(method) {
  if (method === 'card' && !hasBankCard.value) {
    ElMessage.warning('请先添加银行卡后再设为默认银行卡支付')
    prefs.defaultPaymentMethod = getDefaultPaymentMethod('wechat')
    return
  }
  setDefaultPaymentMethod(method)
  ElMessage.success('默认支付方式已更新')
}

async function loadData() {
  try {
    profile.value = await getProfile()
    
    // 确保 vehicles 总是数组，过滤掉 null 值
    const vehiclesData = await getVehicles()
    vehicles.value = Array.isArray(vehiclesData) 
      ? vehiclesData.filter(v => v && v.id)
      : Array.isArray(vehiclesData?.results) 
        ? vehiclesData.results.filter(v => v && v.id)
        : []
    
    loadingRes.value = true
    const resData = await getReservations()
    // 确保 reservations 总是数组，过滤掉 null 值
    reservations.value = Array.isArray(resData)
      ? resData.filter(r => r && r.id)
      : Array.isArray(resData?.results)
        ? resData.results.filter(r => r && r.id)
        : []
  } catch (err) {
    ElMessage.error('数据加载失败')
    // 确保错误时也维持有效的数组状态
    vehicles.value = []
    reservations.value = []
  } finally {
    loadingRes.value = false
  }
}

async function handleSaveProfile() {
  savingProfile.value = true
  try {
    await updateProfile({ email: profile.value.email })
    ElMessage.success('保存成功')
  } catch (err) {
    ElMessage.error('保存失败')
  } finally {
    savingProfile.value = false
  }
}

const handleDeleteCar = (id) => {
  ElMessageBox.confirm('确定要解绑该车辆吗？', '提示', { type: 'warning' })
    .then(async () => {
      await deleteVehicle(id)
      ElMessage.success('解绑成功')
      const vehiclesData = await getVehicles()
      vehicles.value = Array.isArray(vehiclesData) 
        ? vehiclesData.filter(v => v && v.id)
        : Array.isArray(vehiclesData?.results) 
          ? vehiclesData.results.filter(v => v && v.id)
          : []
    }).catch(() => {})
}

const handleSetPrimary = async (id) => {
  try {
    await setPrimaryVehicle(id)
    ElMessage.success('已设为首选车辆')
    const vehiclesData = await getVehicles()
    vehicles.value = Array.isArray(vehiclesData) 
      ? vehiclesData.filter(v => v && v.id)
      : Array.isArray(vehiclesData?.results) 
        ? vehiclesData.results.filter(v => v && v.id)
        : []
  } catch (err) {
    ElMessage.error('设置失败')
  }
}

const handleCancelRes = (id) => {
  ElMessageBox.confirm('确定要取消该预约吗？费用将原路退回。', '取消预约', { type: 'warning' })
    .then(async () => {
      const res = await cancelReservation(id)
      const refundAmount = Number(res?.refund_amount || res?.data?.refund_amount || 0)
      ElMessage.success(refundAmount > 0 ? `预约已取消，已退回 ¥${refundAmount.toFixed(2)}` : '预约已取消')
      const resData = await getReservations()
      reservations.value = Array.isArray(resData)
        ? resData.filter(r => r && r.id)
        : Array.isArray(resData?.results)
          ? resData.results.filter(r => r && r.id)
          : []
    }).catch(() => {})
}

const showAddCarDialog = () => {
  carForm.plate_number = ''
  carForm.energy_type = ''
  addCarDialogVisible.value = true
}

const showEditCarDialog = (car) => {
  editCarForm.plate_number = car.plate_number
  editCarDialogVisible.value = true
}

const resetAddCarDialog = () => {
  carForm.plate_number = ''
  carForm.energy_type = ''
}

const handlePlateComplete = (plateNumber) => {
  carForm.plate_number = plateNumber
  ElMessage.success(`车牌号 ${plateNumber} 输入完成`)
}

const submitAddCar = async () => {
  // 根据能源类型校验车牌号长度
  const expectedLength = carForm.energy_type === 'new_energy' ? 8 : 7
  if (!carForm.plate_number || carForm.plate_number.length !== expectedLength) {
    ElMessage.error(`请完整输入车牌号（${expectedLength}位）`)
    return
  }

  if (!carFormRef.value) return
  await carFormRef.value.validate(async (valid) => {
    if (valid) {
      savingCar.value = true
      try {
        await addVehicle(carForm)
        ElMessage.success('添加车辆成功')
        addCarDialogVisible.value = false
        const vehiclesData = await getVehicles()
        vehicles.value = Array.isArray(vehiclesData) 
          ? vehiclesData.filter(v => v && v.id)
          : Array.isArray(vehiclesData?.results) 
            ? vehiclesData.results.filter(v => v && v.id)
            : []
      } catch (err) {
        // 处理 DRF 可能返回的字段验证错误（例如车牌号已存在）
        const errorData = err.response?.data
        let errorMsg = '添加失败'
        
        if (errorData) {
          if (errorData.detail) {
            errorMsg = errorData.detail
          } else if (typeof errorData === 'object') {
            // 将字段错误拼接成字符串展示
            const messages = []
            for (const key in errorData) {
              const fieldName = key === 'plate_number' ? '车牌号' : key
              messages.push(`${fieldName}: ${errorData[key].join(', ')}`)
            }
            if (messages.length > 0) errorMsg = messages.join(' | ')
          }
        }
        
        ElMessage.error(errorMsg)
      } finally {
        savingCar.value = false
      }
    }
  })
}
</script>
