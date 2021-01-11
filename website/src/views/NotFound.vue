<template>
  <v-row class="px-8 pt-8">
    <v-col>
      <div class="paragraph-text mt-2">
        Strani, ki ste jo zahtevali, ni bilo mogoče najti. Preverite, ali je vnešen naslov pravilen ter poskusite znova.
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

<script lang="ts">
import { configureScope } from '@sentry/vue'
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class NotFound extends Vue {
  created (): void {
    document.title = process.env.VUE_APP_TITLE + ' – Stran ni najdena'
    this.$emit('setPageTitle', process.env.VUE_APP_SHORT + ' – Stran ni najdena')

    if (process.env.VUE_APP_SENTRY_ENABLED === 'true') {
      configureScope(scope => {
        scope.getSpan()?.setHttpStatus(404)
      })
    }
  }
}
</script>
