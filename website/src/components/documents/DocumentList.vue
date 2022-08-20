<!-- Component that displays document list -->

<template>
  <v-expansion-panels v-if="documents.length > 0" tile>
    <v-expansion-panel>
      <v-expansion-panel-header class="text-h6 list-title">{{ title }}</v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-list>
          <v-item-group>
            <v-list-item v-for="(document, id) in documents" :key="id"  two-line>
              <v-list-item-content>
                  <a :href="document.url" style="display: block; text-decoration: none; color: white;"><div><v-list-item-title  class="pl-1">{{ document.title }}</v-list-item-title></div></a>
                  <v-list-item-subtitle>{{ displayDate(document) }}</v-list-item-subtitle>
                  <v-dialog
                    v-model="dialog"
                    width="600px"
                    v-if="document.content"
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        dark
                        v-bind="attrs"
                        v-on="on"
                      >
                        Odpri okrožnico
                      </v-btn>
                    </template>
                    <v-card>
                      <v-card-title>
                        <span class="text-h5">{{ document.title }}</span>
                      </v-card-title >
                      <v-card-text >
                      <div class="con" v-html="document.content"></div>
                      </v-card-text>
                    </v-card>
                  </v-dialog>
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
  @Prop() title!: string
  @Prop() documents!: Document[]

  @Prop() displayedDate!: string
  @Prop() displayDateAsWeek!: boolean

  displayDate (document: Document): string {
    let date

    switch (this.displayedDate) {
      case 'created':
        date = document.created
        break
      case 'modified':
        date = document.modified
        break
      case 'effective':
        date = document.effective
        break
    }

    if (!date) return ''

    if (!this.displayDateAsWeek) return this.formatDate(date)
    else return `${this.formatDate(date)} — ${this.formatEndDate(date)}`
  }

  formatDate (date: string): string {
    return new Date(date).toLocaleDateString('sl')
  }

  formatEndDate (date: string): string {
    return getWeekDays(new Date(date))[4].toLocaleDateString('sl')
  }
}
</script>
