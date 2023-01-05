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
    {
      path: '/',
      name: 'Root',
      component: () => import('../views/RootView.vue')
    },
    {
      path: '/event/:id',
      name: 'Event',
      component: () => import('../views/EventView.vue'),
      props: true
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      props: true
    }
  ]
})

export default router