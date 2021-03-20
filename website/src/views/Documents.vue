<template>
  <div class="documents px-0 pt-0 pt-md-6">
    <document-list :documents="circulars" title="Okrožnice" />
    <document-list :documents="substitutions" class="mt-4" title="Nadomeščanja" />
    <document-list :documents="lunchSchedule" class="mt-4" title="Razporedi delitve kosila" />
    <document-list :documents="menus" class="mt-4" title="Jedilniki" display-week-date="true" />
  </div>
</template>

<style lang="scss">
// Center documents page
.documents {
  margin: 0 auto;
  max-width: 40rem;
}
</style>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import DocumentList from '@/components/documents/DocumentList.vue'
import { Document, StorageModule } from '@/store/modules/storage'

@Component({
  components: { DocumentList }
})
export default class Documents extends Vue {
  get circulars (): Document[] {
    return StorageModule.documents?.filter(document => document.type === 'circular' || document.type === 'other').reverse() || []
  }

  get substitutions (): Document[] {
    return StorageModule.documents?.filter(document => document.type === 'substitutions').reverse() || []
  }

  get lunchSchedule (): Document[] {
    return StorageModule.documents?.filter(document => document.type === 'lunch-schedule').reverse() || []
  }

  get menus (): Document[] {
    return StorageModule.documents?.filter(document => document.type === 'snack-menu' || document.type === 'lunch-menu').reverse() || []
  }

  created (): void {
    document.title = process.env.VUE_APP_TITLE + ' – Okrožnice'
    this.$emit('setPageTitle', process.env.VUE_APP_SHORT + ' – Okrožnice')

    this.$emit('setDayMenuDisplay', false)
    StorageModule.updateDocuments()
  }
}
</script>
