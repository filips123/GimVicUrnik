import { createRouter, createWebHistory } from 'vue-router'
// import { useSettingsStore, EntityType } from '@/stores/settings'

// const settingsStore = useSettingsStore()
// const { entityType } = settingsStore

const Home = () => import('../views/Home.vue')
const Welcome = () => import('../views/Welcome.vue')
const Subscribe = () => import('../views/Subscribe.vue')
const Settings = () => import('../views/Settings.vue')
const Timetable = () => import('../views/Timetable.vue')
const Menus = () => import('../views/Menus.vue')
const Circulars = () => import('../views/Circulars.vue')
const Sources = () => import('../views/Sources.vue')
const NotFound = () => import('../views/NotFound.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      meta: { title: 'Domov' },
      component: Home,
    },
    {
      path: '/welcome',
      name: 'welcome',
      meta: { title: 'Dobrodošli' },
      component: Welcome,
    },
    {
      path: '/subscribe',
      name: 'subscribe',
      meta: { title: 'Naročanje' },
      component: Subscribe,
    },
    {
      path: '/settings',
      name: 'settings',
      meta: { title: 'Nastavitve' },
      component: Settings,
    },
    {
      path: '/timetable/:type?/:value?',
      name: 'timetable',
      meta: { title: 'Urnik' },
      component: Timetable,
    },
    {
      path: '/menus',
      name: 'menus',
      meta: { title: 'Jedilnik' },
      component: Menus,
    },
    {
      path: '/circulars',
      name: 'circulars',
      meta: { title: 'Okrožnice' },
      component: Circulars,
    },
    {
      path: '/sources',
      name: 'sources',
      meta: { title: 'Viri' },
      component: Sources,
    },
    {
      path: '/:pathMatch(.*)',
      name: 'notfound',
      meta: { title: 'Strani ni mogoče najti' },
      component: NotFound,
    },
  ],
})

// router.beforeEach(async (to, from) => {
//   if (entityType == EntityType.None && to.name !== 'welcome') return { name: 'welcome' }
// })

export default router
