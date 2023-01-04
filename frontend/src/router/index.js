import { createRouter, createWebHistory } from 'vue-router'
import LoginView from "@/views/LoginView.vue";
import MarketView from "@/views/MarketView.vue";
import SuccessView from "@/views/SuccessView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/market/:event_id',
      name: 'Market',
      component: MarketView,
      props: true
    },
    {
      path: '/success',
      name: 'Success',
      component: SuccessView
    },
    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue')
    // },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      props: true
    }
  ]
})

export default router
