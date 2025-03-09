import { doc, setDoc } from 'firebase/firestore'
import { getMessaging, getToken } from 'firebase/messaging'
import { defineStore } from 'pinia'
import { useFirestore } from 'vuefire'

import { useSnackbarStore } from '@/composables/snackbar'
import firebaseApp from '@/plugins/firebase'
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

    immediateSubstitutionsNotificationsEnabled: false,
    scheduledSubstitutionsNotificationsEnabled: false,
    scheduledSubstitutionsNotificationsCurrentDayTime: '',
    scheduledSubstitutionsNotificationsNextDayTime: '20:00',

    circularsNotificationsEnabled: false,

    snackMenuNotificationsEnabled: false,
    lunchMenuNotificationsEnabled: false,

    notifications: [] as Notification[],

    seen: true,
  }),

  actions: {
    getFCMToken() {
      const messaging = getMessaging(firebaseApp)
      getToken(messaging, { vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY }).then(
        currentToken => {
          if (currentToken) {
            this.token = currentToken
            this.updateUserFirestoreData()
          } else {
            console.log('Could not get FCM token')
          }
        },
      )
    },

    async updateUserFirestoreData() {
      if (Notification.permission !== 'granted') return

      if (!this.token) {
        this.getFCMToken()
        return
      }

      const { entityType, entityList } = useSettingsStore()

      const db = useFirestore()

      await setDoc(doc(db, 'users', this.token), {
        immediateSubstitutionsNotificationsEnabled: this.immediateSubstitutionsNotificationsEnabled,
        scheduledSubstitutionsNotificationsEnabled: this.scheduledSubstitutionsNotificationsEnabled,
        scheduledSubstitutionsNotificationsCurrentDayTime:
          this.scheduledSubstitutionsNotificationsCurrentDayTime,
        scheduledSubstitutionsNotificationsNextDayTime:
          this.scheduledSubstitutionsNotificationsNextDayTime,

        circularsNotificationsEnabled: this.circularsNotificationsEnabled,

        snackMenuNotificationsEnabled: this.snackMenuNotificationsEnabled,
        lunchMenuNotificationsEnabled: this.lunchMenuNotificationsEnabled,

        entityType: entityType,
        entityList: entityList,
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
