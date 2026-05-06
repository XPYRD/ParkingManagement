<template>
  <!-- 用户管理 -->
  <div class="p-6 lg:p-10 h-full flex flex-col">
    <header class="flex justify-between items-end mb-8 flex-shrink-0">
      <div>
        <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">用户中心</h1>
        <p class="text-secondary text-sm mt-1">管理系统注册用户、车辆绑定与高级订阅状态</p>
      </div>
    </header>

    <div class="flex-1 bg-surface-container-lowest rounded-2xl border border-outline-variant/20 shadow-sm flex flex-col overflow-hidden">
      <!-- 搜索 & 过滤栏 -->
      <div class="p-4 border-b border-outline-variant/20 flex flex-wrap gap-4 items-center justify-between bg-surface-container-low/50">
         <div class="flex gap-4 items-center">
            <el-input v-model="filters.search" placeholder="搜索手机号或用户名..." size="small" class="w-64" clearable @change="loadUsers">
               <template #prefix><span class="material-symbols-outlined text-sm">search</span></template>
            </el-input>
            <el-select v-model="filters.subscription" placeholder="订阅状态" size="small" class="w-32" clearable @change="loadUsers">
               <el-option label="有订阅" value="true" />
               <el-option label="无订阅" value="false" />
            </el-select>
         </div>
      </div>

      <!-- 表格内容 -->
      <div class="flex-1 overflow-auto p-4" v-loading="loading">
        <el-table :data="users" style="width: 100%" stripe>
          <el-table-column label="用户信息" width="220">
             <template #default="{ row }">
                <div class="flex items-center gap-3">
                   <el-avatar :size="36" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                   <div>
                     <p class="font-bold text-sm text-on-surface leading-tight">{{ row.username }}</p>
                     <p class="text-xs text-secondary">{{ row.phone || row.email || '--' }}</p>
                   </div>
                </div>
             </template>
          </el-table-column>
          <el-table-column prop="vehicles_count" label="绑定车辆数" width="100" align="center">
             <template #default="{ row }">
                 <span class="font-bold">{{ row.vehicles_count || 0 }}</span>
             </template>
          </el-table-column>
          <el-table-column label="订阅状态" width="180">
             <template #default="{ row }">
                <el-tag v-if="row.subscription_plan" size="small" type="warning" effect="plain" class="!font-bold !rounded-full text-xs">
                   <span class="material-symbols-outlined text-[10px] mr-0.5">workspace_premium</span>
                   {{ row.subscription_plan }}
                </el-tag>
                <el-tag v-else size="small" type="info" effect="plain" class="!font-bold !rounded-full text-xs">
                   暂无订阅
                </el-tag>
             </template>
          </el-table-column>
          <el-table-column label="注册时间" width="160">
              <template #default="{ row }">
                 {{ row.date_joined ? new Date(row.date_joined).toLocaleString() : '--' }}
              </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
             <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleUserDetail(row)">详情</el-button>
                <el-button link type="danger" size="small" @click="handleFreezeUser(row)">冻结</el-button>
             </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="p-4 border-t border-outline-variant/20 flex justify-end">
         <el-pagination 
            v-model:current-page="currentPage" 
            size="small" 
            background 
            layout="total, prev, pager, next" 
            :total="totalUsers" 
            @current-change="loadUsers"
         />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 用户管理后台 — 真实数据接入API
 */
import { ref, reactive, onMounted } from 'vue'
import { getUsers } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const users = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalUsers = ref(0)
const filters = reactive({
    search: '',
    subscription: ''
})

onMounted(() => {
    loadUsers()
})

const loadUsers = async () => {
    loading.value = true
    try {
        const params = {
           page: currentPage.value,
           ...(filters.search && { search: filters.search }),
           ...(filters.subscription && { has_subscription: filters.subscription })
        }
        const res = await getUsers(params)
        
        if (res.results) {
            users.value = res.results
            totalUsers.value = res.count
        } else {
            users.value = res
            totalUsers.value = res.length
        }
    } catch(err) {
        ElMessage.error('获取用户列表失败')
    } finally {
        loading.value = false
    }
}

const handleUserDetail = (row) => {
    ElMessage.info(`查看用户 ${row.username} 的详情`)
    // 可在此处添加导航或打开详情弹窗
}

const handleFreezeUser = (row) => {
    ElMessageBox.confirm(`确定要冻结用户 ${row.username} 吗？`, '警告', {
        confirmButtonText: '确认冻结',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        ElMessage.success(`用户 ${row.username} 已冻结`)
        // 可在此处调用 API 冻结用户
    }).catch(() => {})
}
</script>
