import { nextTick } from 'vue'
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const Home = () => import('../views/ViewHome.vue')
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
  { path: '/', name: 'home', component: Home },
  // { path: '/timetable/:type?/:value?', name: 'timetable', component: Timetable, meta: { title: 'Urnik' } },
  { path: '/menu', name: 'menu', component: Menu, meta: { title: 'Jedilnik' } },
  { path: '/circulars', name: 'circulars', component: Circulars, meta: { title: 'Okrožnice' } },
  { path: '/sources', name: 'sources', component: Sources, meta: { title: 'Viri' } },
  { path: '/subscribe', name: 'subscribe', component: Subscribe, meta: { title: 'Naročanje' } },
  // { path: '/settings', name: 'settings', component: Settings, meta: { title: 'Nastavitve' } },
  // { path: '/welcome', name: 'welcome', component: Welcome, meta: { title: 'Dobrodošli' } },
  { path: '/:pathMatch(.*)', name: 'notfound', component: NotFound, meta: { title: 'Stran ni najdena' } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Change the document title to the current route title
// We need to use next tick so browser history updates properly
router.afterEach(to => {
  nextTick(() => {
    if (to.meta.title) document.title = to.meta.title + ' – ' + import.meta.env.VITE_TITLE
    else document.title = import.meta.env.VITE_TITLE
  })
})

export default router
