import { nextTick } from 'vue'
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import { homeGuard, timetableGuard } from '@/router/guards'

const Timetable = () => import('../views/ViewTimetable.vue')
const Menu = () => import('../views/ViewMenu.vue')
const Circulars = () => import('../views/ViewCirculars.vue')
const Sources = () => import('../views/ViewSources.vue')
const Subscribe = () => import('../views/ViewSubscribe.vue')
const Settings = () => import('../views/ViewSettings.vue')
const Welcome = () => import('../views/ViewWelcome.vue')
const NotFound = () => import('../views/NotFound.vue')

// prettier-ignore

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: {} },
  { path: '/timetable/:type?/:value?', name: 'timetable', component: Timetable, meta: { title: 'Urnik' } },
  { path: '/menu', name: 'menu', component: Menu, meta: { title: 'Jedilnik' } },
  { path: '/circulars', name: 'circulars', component: Circulars, meta: { title: 'Okrožnice' } },
  { path: '/sources', name: 'sources', component: Sources, meta: { title: 'Viri' } },
  { path: '/subscribe', name: 'subscribe', component: Subscribe, meta: { title: 'Naročanje' } },
  { path: '/settings', name: 'settings', component: Settings, meta: { title: 'Nastavitve' } },
  { path: '/welcome', name: 'welcome', component: Welcome, meta: { title: 'Dobrodošli' } },
  { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFound, meta: { title: 'Stran ni najdena' } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Call the correct route navigation guards
// They need to be global to make sure they are called early
router.beforeEach((to, from) => {
  // Call home guard that redirects the user either to welcome or timetable
  if (to.name === 'home') return homeGuard()

  // Call timetable guard that redirects the user to the correct entity
  if (to.name === 'timetable') return timetableGuard(to, from)
})

// Change the document title to the current route title
// We need to use the next tick so browser history updates properly
router.afterEach(to => {
  nextTick(() => {
    if (to.meta.title) document.title = to.meta.title + ' – ' + import.meta.env.VITE_TITLE
    else document.title = import.meta.env.VITE_TITLE
  })
})

export default router
