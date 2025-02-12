<template>
  <div class="col-start-2 col-span-10">
    <div class="bg-0 dark:bg-950">
      <div class="font-medium text-3xl text-900 dark:text-0 mb-4"></div>
      <div class="text-500 dark:text-300 mb-8"></div>
      <ul class="list-none p-0 m-0">
        <li class="flex items-center py-4 px-2 border-t border flex-wrap">
          <div class="text-500 dark:text-300 w-6/12 md:w-2/12 font-medium"
            >User name</div
          >
          <div
            class="text-900 dark:text-0 w-full md:w-8/12 md:order-none order-1"
          >
            {{ props.user.first_name }} {{ props.user.last_name }}
          </div>
          <div class="w-6/12 md:w-2/12 flex justify-end">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
        <li class="flex items-center py-4 px-2 border-t border flex-wrap">
          <div class="text-500 dark:text-300 w-6/12 md:w-2/12 font-medium"
            >Team members</div
          >
          <div
            class="text-900 dark:text-0 w-full md:w-8/12 md:order-none order-1"
          >
            <Chip
              v-for="u in props.user.team_lead"
              :label="`${u.first_name} ${u.last_name}`"
              class="mr-2"
            ></Chip>
          </div>
          <div class="w-6/12 md:w-2/12 flex justify-end">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
        <li class="flex items-center py-4 px-2 border-t border flex-wrap">
          <div class="text-500 dark:text-300 w-6/12 md:w-2/12 font-medium"
            >Assistants</div
          >
          <div
            class="text-900 dark:text-0 w-full md:w-8/12 md:order-none order-1"
          >
            <Chip
              v-for="u in props.user.manager"
              :label="`${u.first_name} ${u.last_name}`"
              class="mr-2"
            ></Chip>
          </div>
          <div class="w-6/12 md:w-2/12 flex justify-end">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
        <li class="flex items-center py-4 px-2 border-t border flex-wrap">
          <div class="text-500 dark:text-300 w-6/12 md:w-2/12 font-medium"
            >Managed by</div
          >
          <div
            class="text-900 dark:text-0 w-full md:w-8/12 md:order-none order-1"
          >
            {{ user.assistant.first_name }} {{ user.assistant.last_name }}
          </div>
          <div class="w-6/12 md:w-2/12 flex justify-end">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
        <li
          class="flex items-center py-4 px-2 border-t border-b border flex-wrap"
        >
          <div class="text-500 dark:text-300 w-6/12 md:w-2/12 font-medium"
            >Team member of</div
          >
          <div
            class="text-900 dark:text-0 w-full md:w-8/12 md:order-none order-1 leading-normal"
          >
            {{ user.team_member.first_name }} {{ user.team_member.last_name }}
          </div>
          <div class="w-6/12 md:w-2/12 flex justify-end">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
  const props = defineProps({
    user: {
      type: Object,
      required: true
    }
  })
</script>
