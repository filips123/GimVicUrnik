<!-- Component that displays document list -->

<template>
  <v-expansion-panels v-if="documents.length > 0" tile>
    <v-expansion-panel>
      <v-expansion-panel-header class="text-h6 list-title">{{ title }}</v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-list>
          <v-item-group>
            <v-list-item v-for="(substitution, id) in documents" :key="id" :href="substitution.url" two-line>
              <v-list-item-content>
                <v-list-item-title class="pl-1">{{ substitution.description }}</v-list-item-title>
                <v-list-item-subtitle v-if="!displayWeekDate">{{ formatDate(substitution.date) }}</v-list-item-subtitle>
                <v-list-item-subtitle v-else>{{ formatDate(substitution.date) }} — {{ formatEndDate(substitution.date) }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-item-group>
        </v-list>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<style lang="scss">
// Remove horizontal padding from list
.v-expansion-panel-content__wrap {
  padding: 0 0 8px !important;
}

// Change section title line height and padding
.v-expansion-panel-header {
  line-height: 1rem !important;
  min-height: 48px !important;
  padding: 0 24px !important;
}

// Change font weight
.list-title {
  font-weight: 400 !important;
}

// Fix padding of title and subtitle
.v-list-item__title, .v-list-item__subtitle {
  padding-left: 4px !important;
}
</style>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { Document } from '@/store/modules/storage'
import { getWeekDays } from '@/utils/days'

@Component
export default class DocumentList extends Vue {
  @Prop() displayWeekDate!: boolean
  @Prop() title!: string
  @Prop() documents!: Document[]

  formatDate (date: string): string {
    return new Date(date).toLocaleDateString('sl')
  }

  formatEndDate (date: string): string {
    return getWeekDays(new Date(date))[4].toLocaleDateString('sl')
  }
}
</script>
