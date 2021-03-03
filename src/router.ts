import _ from 'lodash'
import Assets from '@/components/assets/Assets.vue'
import BaseView from '@/components/BaseView.vue'
import Error from '@/components/Error.vue'
import NotFound from '@/components/NotFound.vue'
import Router from 'vue-router'
import Squiggy from '@/components/Squiggy.vue'
import Vue from 'vue'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/squiggy'
    },
    {
      path: '/',
      component: BaseView,
      children: [
        {
          path: '/squiggy',
          component: Squiggy,
          meta: {
            title: 'Hello!'
          },
          name: 'Squiggy'
        },
        {
          path: '/assets',
          component: Assets,
          meta: {
            title: 'Assets'
          },
          name: 'Assets'
        }
      ]
    },
    {
      path: '/',
      component: BaseView,
      children: [
        {
          path: '/404',
          component: NotFound,
          meta: {
            title: 'Page not found'
          }
        },
        {
          path: '/error',
          component: Error,
          meta: {
            title: 'Error'
          }
        },
        {
          path: '*',
          redirect: '/404'
        }
      ]
    }
  ]
})

router.afterEach((to: any) => {
  const pageTitle = _.get(to, 'meta.title')
  document.title = `${pageTitle || _.capitalize(to.name) || 'Welcome'} | SuiteC`
  Vue.prototype.$announcer.assertive(`${pageTitle || 'Page'} is loading`)
})

export default router
