import { doc, setDoc } from 'firebase/firestore'
import { defineStore } from 'pinia'
import { useFirestore } from 'vuefire'

import { useSnackbarStore } from '@/composables/snackbar'
import router from '@/router'
import { useSettingsStore } from '@/stores/settings'
import { updateWrapper } from '@/utils/update'

export interface Notification {
  date: string
  title: string
  content: string | null
}

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    token: '',

    substitutionsNotificationsImmediate: false,
    substitutionsNotificationsSetTime: false,
    substitutionsNotificationsCurrentDayTime: '07:00',
    substitutionsNotificationsNextDayTime: '',

    circularsNotificationsEnabled: false,

    snackMenuNotificationsEnabled: false,
    lunchMenuNotificationsEnabled: false,

    notifications: [] as Notification[],

    seen: true,
  }),

  actions: {
    async updateUserFirestoreData() {
      if (!this.token) return

      const { entityList, snackType, lunchType } = useSettingsStore()

      const db = useFirestore()

      await setDoc(doc(db, 'users', this.token), {
        substitutionsNotificationsImmediate: this.substitutionsNotificationsImmediate,
        substitutionsNotificationsSetTime: this.substitutionsNotificationsSetTime,
        substitutionsNotificationsCurrentDayTime: this.substitutionsNotificationsCurrentDayTime,
        substitutionsNotificationsNextDayTime: this.substitutionsNotificationsNextDayTime,

        circularsNotificationsEnabled: this.circularsNotificationsEnabled,

        snackMenuNotificationsEnabled: this.snackMenuNotificationsEnabled,
        lunchMenuNotificationsEnabled: this.lunchMenuNotificationsEnabled,

        entityList: entityList,
        snackType: snackType,
        lunchType: lunchType,
      })
    },

    async updateNotifications() {
      await updateWrapper(async () => {
        const response = await fetch(import.meta.env.VITE_API + '/notifications')
        const notifications = await response.json()

        const latestNotificationDate = new Date(notifications[notifications.length - 1].date)

        // Display the snackbar if new notifications were sent and are not older than 14 days
        if (
          notifications.length > this.notifications.length &&
          latestNotificationDate >= new Date(Date.now() - 14 * 24 * 60 * 60 * 1000)
        ) {
          const snackbarStore = useSnackbarStore()

          snackbarStore.displaySnackbar(
            'Novo obvestilo uporabnikom',
            'Oglej',
            () => router.push({ path: '/notifications' }),
            -1,
          )

          this.seen = false
        }

        this.notifications = notifications.reverse()
      })
    },
  },

  persist: true,
})
