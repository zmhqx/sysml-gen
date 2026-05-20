import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login/index.vue'),
    },
    {
      path: '/',
      component: () => import('../views/Layout.vue'),
      redirect: '/home',
      children: [
        {
          path: 'home',
          name: 'Home',
          component: () => import('../views/Home/index.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'project',
          name: 'ProjectList',
          component: () => import('../views/Project/index.vue'),
          meta: { title: '项目管理' },
        },
        {
          path: 'project/:id',
          name: 'ProjectDetail',
          component: () => import('../views/Project/Detail.vue'),
          meta: { title: '项目详情' },
        },
        {
          path: 'model',
          name: 'ModelList',
          component: () => import('../views/Model/index.vue'),
          meta: { title: '模型管理' },
        },
        {
          path: 'model/:id',
          name: 'ModelDetail',
          component: () => import('../views/Model/Detail.vue'),
          meta: { title: '模型详情' },
        },
        {
          path: 'model/:id/view',
          name: 'ModelView',
          component: () => import('../views/Model/View.vue'),
          meta: { title: '模型视图' },
        },
        {
          path: 'model/:id/editor',
          name: 'ModelEditor',
          component: () => import('../views/Model/Editor.vue'),
          meta: { title: '视图编辑器' },
        },
        {
          path: 'template',
          name: 'TemplateList',
          component: () => import('../views/Template/index.vue'),
          meta: { title: '模板管理' },
        },
        {
          path: 'document',
          name: 'DocumentList',
          component: () => import('../views/Document/index.vue'),
          meta: { title: '文档管理' },
        },
        {
          path: 'document/generate',
          name: 'DocumentGenerate',
          component: () => import('../views/Document/Generate.vue'),
          meta: { title: '生成文档' },
        },
        {
          path: 'document/:id',
          name: 'DocumentPreview',
          component: () => import('../views/Document/Preview.vue'),
          meta: { title: '文档预览' },
        },
        {
          path: 'admin/user',
          name: 'AdminUser',
          component: () => import('../views/Admin/User.vue'),
          meta: { title: '用户管理', admin: true },
        },
        {
          path: 'admin/log',
          name: 'AdminLog',
          component: () => import('../views/Admin/Log.vue'),
          meta: { title: '日志管理', admin: true },
        },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/home')
  } else {
    next()
  }
})

export default router
