<!-- 后台管理页 Admin -->
<script setup>
import { ref, computed, onMounted, h } from 'vue'
import {
  NTabs, NTabPane, NCard, NStatistic, NDataTable, NButton,
  NModal, NForm, NFormItem, NInput, NSelect, NSpace, NGrid, NGi,
  NPopconfirm, NTag, useMessage
} from 'naive-ui'
import ajax from '@/api/ajax'
import {
  reqUserList, reqUpdateUser, reqDelUser,
  reqAuthorityList, reqUpdateAuthority, reqDelAuthority
} from '@/api/baseAPI'

definePageMeta({ middleware: 'auth' })

const message = useMessage()
const users = ref([])
const authorities = ref([])
const loading = ref(false)

const userCount = computed(() => users.value.length)
const roleCount = computed(() => authorities.value.length)
const authorityOptions = computed(() =>
  authorities.value.map(a => ({ label: a.name, value: a.name }))
)

// --- User Management ---
const showUserModal = ref(false)
const isEditingUser = ref(false)
const userForm = ref({ username: '', password: '', authority: '' })

const userColumns = [
  { title: '用户名', key: 'username' },
  {
    title: '角色', key: 'authority',
    render: (row) => h(NTag, { type: 'info', bordered: false }, { default: () => row.authority || '无' })
  },
  {
    title: '操作', key: 'actions',
    render(row) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'small', type: 'primary', secondary: true, onClick: () => editUser(row) }, { default: () => '编辑' }),
          h(NPopconfirm, { onPositiveClick: () => deleteUser(row.username) }, {
            trigger: () => h(NButton, { size: 'small', type: 'error', secondary: true }, { default: () => '删除' }),
            default: () => `确定删除用户 "${row.username}" 吗？`
          })
        ]
      })
    }
  }
]

function openAddUser() {
  isEditingUser.value = false
  userForm.value = { username: '', password: '', authority: '' }
  showUserModal.value = true
}

function editUser(user) {
  isEditingUser.value = true
  userForm.value = { username: user.username, password: '', authority: user.authority }
  showUserModal.value = true
}

async function submitUser() {
  const { username, password, authority } = userForm.value
  if (!username) { message.error('请输入用户名'); return }
  if (!isEditingUser.value && !password) { message.error('请输入密码'); return }
  try {
    let res
    if (isEditingUser.value && !password) {
      res = await ajax('/api/user', { type: 'update', username, password: '', authority }, 'POST')
    } else {
      res = await reqUpdateUser(username, password, authority)
    }
    if (res.status === '0') {
      message.success(isEditingUser.value ? '更新成功' : '创建成功')
      showUserModal.value = false
      await loadData()
    }
  } catch { message.error('操作失败') }
}

async function deleteUser(username) {
  try {
    const res = await reqDelUser(username)
    if (res.status === '0') { message.success('删除成功'); await loadData() }
  } catch { message.error('删除失败') }
}

// --- Role Management ---
const showRoleModal = ref(false)
const isEditingRole = ref(false)
const roleForm = ref({ name: '', menus: '' })

const roleColumns = [
  { title: '角色名称', key: 'name' },
  { title: '菜单权限', key: 'menus', render: (row) => row.menus || '无' },
  {
    title: '操作', key: 'actions',
    render(row) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'small', type: 'primary', secondary: true, onClick: () => editRole(row) }, { default: () => '编辑' }),
          h(NPopconfirm, { onPositiveClick: () => deleteRole(row.name) }, {
            trigger: () => h(NButton, { size: 'small', type: 'error', secondary: true }, { default: () => '删除' }),
            default: () => `确定删除角色 "${row.name}" 吗？`
          })
        ]
      })
    }
  }
]

function openAddRole() {
  isEditingRole.value = false
  roleForm.value = { name: '', menus: '' }
  showRoleModal.value = true
}

function editRole(role) {
  isEditingRole.value = true
  roleForm.value = { name: role.name, menus: role.menus }
  showRoleModal.value = true
}

async function submitRole() {
  const { name, menus } = roleForm.value
  if (!name) { message.error('请输入角色名称'); return }
  try {
    const res = await reqUpdateAuthority(name, menus)
    if (res.status === '0') {
      message.success(isEditingRole.value ? '更新成功' : '创建成功')
      showRoleModal.value = false
      await loadData()
    }
  } catch { message.error('操作失败') }
}

async function deleteRole(name) {
  try {
    const res = await reqDelAuthority(name)
    if (res.status === '0') { message.success('删除成功'); await loadData() }
  } catch { message.error('删除失败') }
}

// --- Load Data ---
async function loadData() {
  loading.value = true
  try {
    const [userRes, authRes] = await Promise.all([reqUserList(), reqAuthorityList()])
    if (userRes.status === '0') users.value = userRes.data || []
    if (authRes.status === '0') authorities.value = authRes.data || []
  } catch { message.error('数据加载失败') }
  loading.value = false
}

onMounted(loadData)
</script>
<template>
  <div class="admin-container">
    <div class="admin-card">
      <n-tabs type="line" animated>
        <n-tab-pane name="dashboard" tab="总览">
          <n-grid :cols="2" :x-gap="16" :y-gap="16">
            <n-gi>
              <n-card><n-statistic label="用户总数" :value="userCount" /></n-card>
            </n-gi>
            <n-gi>
              <n-card><n-statistic label="角色总数" :value="roleCount" /></n-card>
            </n-gi>
          </n-grid>
        </n-tab-pane>

        <n-tab-pane name="users" tab="用户管理">
          <div class="section-header">
            <span />
            <n-button type="primary" @click="openAddUser">新增用户</n-button>
          </div>
          <n-data-table :columns="userColumns" :data="users" :loading="loading" :row-key="row => row.username" />
        </n-tab-pane>

        <n-tab-pane name="roles" tab="角色管理">
          <div class="section-header">
            <span />
            <n-button type="primary" @click="openAddRole">新增角色</n-button>
          </div>
          <n-data-table :columns="roleColumns" :data="authorities" :loading="loading" :row-key="row => row.name" />
        </n-tab-pane>
      </n-tabs>
    </div>

    <!-- User Modal -->
    <n-modal v-model:show="showUserModal" preset="card" :title="isEditingUser ? '编辑用户' : '新增用户'" style="width: 450px;">
      <n-form>
        <n-form-item label="用户名">
          <n-input v-model:value="userForm.username" :disabled="isEditingUser" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="userForm.password" type="password" show-password-on="click"
            :placeholder="isEditingUser ? '留空则不修改密码' : '请输入密码'" />
        </n-form-item>
        <n-form-item label="角色">
          <n-select v-model:value="userForm.authority" :options="authorityOptions" placeholder="请选择角色" clearable />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="showUserModal = false">取消</n-button>
          <n-button type="primary" @click="submitUser">确定</n-button>
        </n-space>
      </template>
    </n-modal>
    <!-- Role Modal -->
    <n-modal v-model:show="showRoleModal" preset="card" :title="isEditingRole ? '编辑角色' : '新增角色'" style="width: 450px;">
      <n-form>
        <n-form-item label="角色名称">
          <n-input v-model:value="roleForm.name" :disabled="isEditingRole" placeholder="请输入角色名称" />
        </n-form-item>
        <n-form-item label="菜单权限">
          <n-input v-model:value="roleForm.menus" type="textarea" placeholder="请输入菜单权限" :rows="3" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="showRoleModal = false">取消</n-button>
          <n-button type="primary" @click="submitRole">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.admin-container {
  display: flex;
  justify-content: center;
  padding: 80px 20px 40px;
}

.admin-card {
  width: 100%;
  max-width: 900px;
  background: var(--color-background);
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}
</style>
