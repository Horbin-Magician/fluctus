import {createRouter, createWebHistory} from 'vue-router'

const routes = [
  { path: '/', component: () => import('./pages/HomePage.vue')},
  { path: '/about', component: () => import('./pages/AboutPage.vue') },
  { path: '/repository', component: () => import('./pages/RepositoryPage.vue') },

  { path: '/calendar', component: () => import('./pages/CalendarPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes, // `routes: routes` 的缩写
})

export default router;