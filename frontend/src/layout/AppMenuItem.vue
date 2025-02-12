<template>
  <div>
    <router-link
      v-if="item.to"
      :to="item.to"
      @click="routerLinkEmitClosed(item, $event)"
      :class="[menuItemClass, activeClass(item)]"
      :aria-label="item.label"
      style="text-decoration: none"
      v-styleclass="{
        selector: '#app-sidebar-9',
        leaveActiveClass: '',
        leaveToClass: 'hidden'
      }"
      v-ripple
    >
      <i
        :class="`pi ${item.icon} mr-2 lg:mr-0 mb-0 lg:mb-2`"
        style="font-size: 1.8rem"
      ></i>
      <span class="inline text-2xl font-large lg:text-lg lg:block">{{
        item.label
      }}</span>
    </router-link>
    <a
      v-else
      @click="routerLinkEmitClosedElse(item, $event)"
      :class="[menuItemClass, activeClass(item)]"
      v-ripple
      v-styleclass="{
        selector: '#app-sidebar-9',
        leaveActiveClass: '',
        leaveToClass: 'hidden'
      }"
    >
      <i
        :class="`pi ${item.icon} mr-2 lg:mr-0 mb-0 lg:mb-2 `"
        style="font-size: 1.8rem"
      ></i>
      <span class="inline text-2xl font-large lg:text-lg lg:block">{{
        item.label
      }}</span>
    </a>
  </div>
</template>

<script setup>
  import { ref, onBeforeMount, watch, defineEmits } from "vue"
  import { useRoute } from "vue-router"
  import { useLayout } from "@/layout/composables/layout"
  import { useUsers } from "../store/modules/users"
  import { usesSwitchToOrdersHelper } from "@/store/modules/switchToOrdersHelper"
  const switchToOrdersHelper = usesSwitchToOrdersHelper()

  const route = useRoute()

  const { layoutConfig, layoutState, setActiveMenuItem, onMenuToggle } =
    useLayout()

  const props = defineProps({
    item: {
      type: Object,
      default: () => ({})
    },
    index: {
      type: Number,
      default: 0
    },
    root: {
      type: Boolean,
      default: true
    },
    parentItemKey: {
      type: String,
      default: null
    }
  })

  const usersStore = useUsers()

  const isActiveMenu = ref(false)
  const itemKey = ref(null)
  const emit = defineEmits(["closed"])
  onBeforeMount(() => {
    // itemKey.value = props.parentItemKey ? props.parentItemKey + '-' + props.index : String(props.index);
    // const activeItem = layoutState.activeMenuItem;
    // isActiveMenu.value = activeItem === itemKey.value || activeItem
  })

  // watch(
  //     () => layoutConfig.activeMenuItem.value,
  //     (newVal) => {
  //         isActiveMenu.value = newVal === itemKey.value || newVal.startsWith(itemKey.value + '-');
  //     }
  // );
  const itemClick = (event, item) => {
    if (item.redirect) {
      window.open(item.redirect, "_blank")
    }

    if (item.label == "Orders") {
      switchToOrdersHelper.switchToOrders()
    }

    setActiveMenuItem(itemKey)
  }

  const routerLinkEmitClosed = (item, $event) => {
    emit("closed")
    itemClick($event, item)
  }

  const routerLinkEmitClosedElse = (item, $event) => {
    emit("closed")
    itemClick($event, item)
  }

  const checkActiveRoute = (item) => {
    return route.path === item.to
  }

  const activeClass = (item) => {
    const color = usersStore.darkMode.value
      ? "text-blue-400 border-blue-400"
      : "text-blue-500 border-blue-500"
    return checkActiveRoute(item) ? color : ""
  }

  const menuItemClass = [
    "flex",
    "flex-row",
    "lg:flex-col",
    "items-center",
    "cursor-pointer",
    "p-4",
    "lg:justify-center",
    "border-l-2",
    "hover:border-300 dark:hover:border-500",
    "duration-150",
    "p-ripple"
  ]
</script>

<style lang="scss" scoped></style>
