import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'

Vue.use(VueRouter)

const Home = () => import(/* webpackChunkName: "home" */ '../views/Home.vue')
const NotFound = () => import(/* webpackChunkName: "notfound" */ '../views/NotFound.vue')
const Welcome = () => import(/* webpackChunkName: "welcome" */ '../views/Welcome.vue')
const Settings = () => import(/* webpackChunkName: "settings" */ '../views/Settings.vue')
const Timetable = () => import(/* webpackChunkName: "timetable" */ '../views/Timetable.vue')
const Menus = () => import(/* webpackChunkName: "menus" */ '../views/Menus.vue')
const Documents = () => import(/* webpackChunkName: "documents" */ '../views/Documents.vue')

const routes: Array<RouteConfig> = [
  { path: '/', name: 'home', component: Home },
  { path: '*', name: 'notfound', component: NotFound },
  { path: '/welcome', name: 'welcome', component: Welcome },
  { path: '/settings', name: 'settings', component: Settings },
  { path: '/timetable/:type?/:value?', name: 'timetable', component: Timetable },
  { path: '/menus', name: 'menus', component: Menus },
  { path: '/documents', name: 'documents', component: Documents }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
