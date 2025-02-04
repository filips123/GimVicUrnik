import { nextTick } from 'vue'
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import { homeGuard, timetableGuard, welcomeGuard } from '@/router/guards'
import { useSessionStore } from '@/stores/session'

const Timetable = () => import('../views/ViewTimetable.vue')
const Menu = () => import('../views/ViewMenu.vue')
const Circulars = () => import('../views/ViewCirculars.vue')
const Sources = () => import('../views/ViewSources.vue')
const Subscribe = () => import('../views/ViewSubscribe.vue')
const Notifications = () => import('../views/ViewNotifications.vue')
const Settings = () => import('../views/ViewSettings.vue')
const Welcome = () => import('../views/ViewWelcome.vue')
const NotFound = () => import('../views/NotFound.vue')

// prettier-ignore

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: {} },
  { path: '/', name: 'welcome', component: Welcome, meta: { title: import.meta.env.VITE_TITLE } },
  { path: '/timetable/:type?/:value?', name: 'timetable', component: Timetable, meta: { title: 'Urnik', allowPullToRefresh: true, showDayTabs: true, showEntityName: true } },
  { path: '/menu', name: 'menu', component: Menu, meta: { title: 'Jedilnik', allowPullToRefresh: true, showDayTabs: true } },
  { path: '/circulars', name: 'circulars', component: Circulars, meta: { title: 'Okrožnice', allowPullToRefresh: true } },
  { path: '/sources', name: 'sources', component: Sources, meta: { title: 'Viri', allowPullToRefresh: true } },
  { path: '/subscribe', name: 'subscribe', component: Subscribe, meta: { title: 'Naročanje' } },
  { path: '/notifications', name: 'notifications', component: Notifications, meta: { title: 'Sporočila' } },
  { path: '/settings', name: 'settings', component: Settings, meta: { title: 'Nastavitve' } },
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

  // Call welcome guard that redirects the user to timetable if it has the entity set
  // Included just in case the route priority changes and welcome is matched first
  if (to.name === 'welcome') return welcomeGuard()

  // Call timetable guard that redirects the user to the correct entity
  if (to.name === 'timetable') return timetableGuard(to, from)
})

// Change the document title to the current route title
// We need to use the next tick so browser history updates properly
router.afterEach(to => {
  nextTick(() => {
    if (!to.meta.title || to.meta.title === import.meta.env.VITE_TITLE) {
      document.title = import.meta.env.VITE_TITLE
      return
    }

    if (to.meta.showEntityName) {
      const { currentEntityList } = useSessionStore()
      document.title = `${to.meta.title} – ${currentEntityList.join(', ')} – ${import.meta.env.VITE_TITLE}`
    } else {
      document.title = `${to.meta.title} – ${import.meta.env.VITE_TITLE}`
    }
  })
})

export default router
