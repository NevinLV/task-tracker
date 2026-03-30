import type { RouteRecordRaw } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ProfileView from '@/views/ProfileView.vue'
import TasksListView from '@/views/TasksListView.vue'
import TaskEditView from '@/views/TaskEditView.vue'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/tasks',
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guest: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks',
    name: 'tasks',
    component: TasksListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks/new',
    name: 'task-new',
    component: TaskEditView,
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks/:id',
    name: 'task-edit',
    component: TaskEditView,
    meta: { requiresAuth: true },
  },
]
