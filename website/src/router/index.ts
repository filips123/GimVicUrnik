import { EntityType, useSettingsStore } from '@/stores/settings'
import { createRouter, createWebHistory } from 'vue-router'

const Home = () => import('../views/ViewHome.vue')
const Welcome = () => import('../views/ViewWelcome.vue')
const Subscribe = () => import('../views/ViewSubscribe.vue')
const Settings = () => import('../views/ViewSettings.vue')
const Timetable = () => import('../views/ViewTimetable.vue')
const Menu = () => import('../views/ViewMenu.vue')
const Circulars = () => import('../views/ViewCirculars.vue')
const Sources = () => import('../views/ViewSources.vue')
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
      path: '/menu',
      name: 'menu',
      meta: { title: 'Jedilnik' },
      component: Menu,
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
      meta: { title: 'Stran ni najdena' },
      component: NotFound,
    },
  ],
})

router.beforeEach(async (to) => {
  const settingsStore = useSettingsStore()
  const { entityType } = settingsStore

  document.title = import.meta.env.VITE_TITLE + ' - ' + to.meta.title

  if (entityType === EntityType.None && to.name !== 'welcome') return { name: 'welcome' }
})

export default router
