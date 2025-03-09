<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import { type Notification } from '@/stores/notifications'
import { useNotificationsStore } from '@/stores/notifications'
import { localizeDate } from '@/utils/localization'

const { notifications } = storeToRefs(useNotificationsStore())

const contentDialog = ref(false)
const selected = ref({} as Notification)

function handleDialog(clickedNotification: Notification) {
  selected.value = clickedNotification
  contentDialog.value = true
}
</script>

<template>
  <v-column>
    <v-lazy v-for="notification in notifications" :key="notification.title" height="48">
      <v-list-item
        :title="notification.title"
        :subtitle="localizeDate(notification.date)"
        :aria-label="notification.title"
        class="notification-item"
        height="48"
        @[notification.content&&`click`]="handleDialog(notification)"
      >
      </v-list-item>
    </v-lazy>
  </v-column>

  <v-dialog v-model="contentDialog">
    <v-card :title="selected.title" :text="selected.content!">
      <template #actions>
        <v-btn text="V redu" @click="contentDialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>

<style>
/* Make items correctly positioned */

.notification-item {
  padding: 0;
}

.notification-item > .v-list-item__overlay {
  border-radius: 4px;
  margin-left: -8px;
  margin-right: -8px;
}

.notification-item::after,
.notification-item .v-ripple__container {
  border-radius: 4px;
  width: calc(100% + 16px);
  left: -8px;
}

.notification-item .v-ripple__animation {
  left: 8px;
  scale: 1.2;
}
</style>
