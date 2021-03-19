<template>
  <div class="menus px-0 pt-0 pt-md-6">
    <menu-display v-for="(value, index) in documents"
      :key="value.date"
      :class="{ 'mt-4': index > 0}"
      :date="value.date"
      :lunch-schedule="value.lunchSchedule"
      :menu="value.menu" />
  </div>
</template>

<style lang="scss">
// Center menus page
.menus {
  margin: 0 auto;
  max-width: 40rem;
}
</style>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import MenuDisplay from '@/components/menus/MenuDisplay.vue'
import { LunchSchedule, Menu, StorageModule } from '@/store/modules/storage'

@Component({
  components: { MenuDisplay }
})
export default class Menus extends Vue {
  get documents (): { date: string, lunchSchedule: LunchSchedule[], menu: Menu }[] {
    if (!StorageModule.lunchSchedule || !StorageModule.menus) return []

    const data: { date: string, lunchSchedule: LunchSchedule[], menu: Menu }[] = []
    for (let i = 0; i < (StorageModule.lunchSchedule.length || 0); i++) {
      const date = StorageModule.lunchSchedule[i][0]
      const lunchSchedule = StorageModule.lunchSchedule[i][1]
      const menu = StorageModule.menus[i][1]

      data.push({ date, lunchSchedule, menu })
    }

    return data
  }

  created (): void {
    document.title = process.env.VUE_APP_TITLE + ' – Jedilnik'
    this.$emit('setPageTitle', process.env.VUE_APP_SHORT + ' – Jedilnik')
  }
}
</script>
