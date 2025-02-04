import { doc, setDoc } from 'firebase/firestore'
import { defineStore } from 'pinia'
import { useFirestore } from 'vuefire'

import { useSettingsStore } from './settings'

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
  },

  persist: true,
})
