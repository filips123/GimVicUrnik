<!-- Component that displays document list -->

<template>
  <v-expansion-panels v-if="documents.length > 0" tile>
    <v-expansion-panel>
      <v-expansion-panel-header class="text-h6 list-title">{{ title }}</v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-list>
          <v-item-group>
            <v-list-item v-for="(document, id) in documents" :key="id" :href="tokenizeUrl(document.url)" two-line>
              <v-list-item-content>
                <v-list-item-title class="pl-1">{{ document.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ displayDate(document) }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-dialog v-model="documentDialogs[id]" v-if="document.content" scrollable width="42rem">
                <template #activator="{ on: dialog }">
                  <v-tooltip top>
                    <template #activator="{ on: tooltip }">
                      <v-btn icon v-on="{ ...tooltip, ...dialog }" @click.prevent>
                        <v-icon dark>{{ mdiTextBoxOutline }}</v-icon>
                      </v-btn>
                    </template>
                    <span>Odpri besedilo dokumenta</span>
                  </v-tooltip>
                </template>
                <v-card>
                  <v-card-title>
                    <span class="text-h5 word-wrap">{{ document.title }}</span>
                  </v-card-title>
                  <v-card-text>
                    <div class="con" v-html="document.content"></div>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="green" text @click="$set(documentDialogs, id, false)">Zapri</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
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

// Wrap text by words
.word-wrap {
  word-break: break-word;
}

// Fix padding of title and subtitle
.v-list-item__title, .v-list-item__subtitle {
  padding-left: 4px !important;
}
</style>

<script lang="ts">
import { mdiTextBoxOutline } from '@mdi/js'
import { Component, Prop, Vue } from 'vue-property-decorator'

import { SettingsModule } from '@/store/modules/settings'
import { Document } from '@/store/modules/storage'
import { getWeekDays } from '@/utils/days'

@Component
export default class DocumentList extends Vue {
  mdiTextBoxOutline = mdiTextBoxOutline

  @Prop() title!: string
  @Prop() documents!: Document[]

  @Prop() displayedDate!: string
  @Prop() displayDateAsWeek!: boolean

  documentDialogs = {}

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

  tokenizeUrl (url: string): string {
    const pluginFileWebserviceUrl = process.env.VUE_APP_ECLASSROOM_WEBSERVICE
    const pluginFileNormalUrl = process.env.VUE_APP_ECLASSROOM_NORMAL
    const moodleToken = SettingsModule.moodleToken

    if (moodleToken && url.includes(pluginFileNormalUrl)) {
      return url
        .replace(pluginFileNormalUrl, pluginFileWebserviceUrl) +
        `?token=${moodleToken}`
    }

    return url
  }
}
</script>
