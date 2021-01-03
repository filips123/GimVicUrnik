<template>
  <v-row class="px-8 pt-8">
    <v-col>
      <div class="paragraph-text mt-2">
        Not implemented yet.
      </div>
    </v-col>
  </v-row>
</template>

<style lang="scss">
// Configure font size
.paragraph-text {
  font-size: 18px;
}
</style>

<!-- TODO: Display documents (announcements, substitutions, circulars, menus...) -->

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class Documents extends Vue {
  created (): void {
    document.title = process.env.VUE_APP_TITLE + ' – Okrožnice'
    this.$emit('setPageTitle', process.env.VUE_APP_SHORT + ' – Okrožnice')
  }
}
</script>
