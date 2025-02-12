<template>
  <div class="relative flex min-h-screen lg:static bg-50 dark:bg-950">
    <!-- <router-view v-if="$route.currentRoute.value.name === 'payment'" /> -->
    <Payment v-if="$isPayment" />
    <div
      v-if="state.showLogin && !$isPayment && !$isPublic"
      class="flex flex-col items-center w-full"
    >
      <div class="pt-16 mt-16">
        <img :src="$logoPath" alt="Image" width="100" />
      </div>
      <div class="mt-6">
        <h1 class="text-2xl text-700 dark:text-100">Welcome to {{ $title }}</h1>
      </div>

      <div class="mt-2">
        <Button
          label="Login"
          class="p-button-lg"
          @click="auth0.loginWithRedirect()"
        />
      </div>
    </div>

    <div
      v-if="
        !state.showLogin && !$isPayment && !$isPublic && auth0.isAuthenticated
      "
      id="app-sidebar-1"
      class="absolute top-0 left-0 flex-shrink-0 hidden h-screen select-none surface-section lg:block lg:static z-1 border-right-1 surface-border"
    >
      <Drawer v-model:visible="visibleLeft">
        <template #container="{ closeCallback }">
          <app-menu @closed="closeCallback"></app-menu>
        </template>
      </Drawer>
      <app-menu v-if="!smAndSmaller"></app-menu>
    </div>
    <div
      v-if="
        (!state.showLogin && !$isPayment && auth0.isAuthenticated) || $isPublic
      "
      class="w-full"
    >
      <div>
        <div
          class="flex flex-col items-center w-full col-span-1 lg:static"
          :style="smAndSmaller ? 'height: 2rem' : ''"
        >
          <a
            v-if="!$isPublic"
            @click="visibleLeft = true"
            v-ripple
            class="block mr-4 cursor-pointer lg:hidden text-700 dark:text-100 p-ripple"
            v-styleclass="{
              selector: '#app-sidebar-9',
              enterClass: 'hidden',
              enterActiveClass: 'animate-fadeinleft',
              leaveToClass: 'hidden',
              leaveActiveClass: 'animate-fadeoutleft',
              hideOnOutsideClick: true
            }"
          >
            <i class="text-4xl pi pi-bars"> </i>
          </a>
        </div>

        <div
          class="flex justify-end pr-12 mt-2 mr-12"
          :class="{
            'ml-1': smAndSmaller,
            'bg-red-100': $isPublic === false && usersStore?.cms?.id === 5
          }"
        >
          <div
            v-if="!smAndSmaller"
            class="flex flex-row items-center space-x-4"
          >
            <div class="flex flex-row items-center space-x-4">
              <div class="font-medium text-gray-900 dark:text-white">
                {{ usersStore.currentUser?.full_name }} ({{
                  usersStore.currentUser?.role_name
                }}
                )
              </div>
              <span
                class="text-sm font-medium text-gray-600 dark:text-gray-200"
              >
                {{ usersStore?.cms?.account_name }}
              </span>
            </div>

            <div class="flex items-center space-x-1">
              <Select
                v-if="$ability.can('update', 'usac_switch_accounts')"
                v-model="selectedAccount.id"
                :options="[
                  {
                    label: 'USA Containers',
                    value: 1
                  },
                  {
                    label: 'USA Containers Canada',
                    value: 5
                  }
                ]"
                optionLabel="label"
                optionValue="value"
                placeholder="Switch Account"
              >
              </Select>
            </div>

            <div class="flex items-center space-x-2">
              <AutoComplete
                v-if="
                  $ability.can('update', 'can_emulate_users') ||
                  usersStore.isEmulating
                "
                v-model="selectedUser"
                @click="getUsers"
                :loading="state.loadingUsers"
                :suggestions="filteredMappedUsers"
                @complete="search"
                optionLabel="label"
                optionValue="value"
                placeholder="Emulate User"
              />
              <Button
                v-if="usersStore.isEmulating"
                class=""
                @click="stopEmulating"
              >
                Reset
              </Button>
            </div>

            <div class="flex items-center space-x-4">
              <button
                @click="usersStore.darkMode = !usersStore.darkMode"
                class="bg-transparent border-none"
              >
                <i
                  style="font-size: 1.5rem"
                  :class="[
                    'pi',
                    {
                      'pi-moon': usersStore.darkMode,
                      'pi-sun': !usersStore.darkMode
                    }
                  ]"
                ></i>
              </button>
            </div>
          </div>
          <div v-else class="flex flex-col items-center mt-4">
            <Select
              v-if="$ability.can('update', 'usac_switch_accounts')"
              v-model="selectedAccount.id"
              :options="[
                {
                  label: 'USA Containers',
                  value: 1
                },
                {
                  label: 'USA Containers Canada',
                  value: 5
                }
              ]"
              optionLabel="label"
              optionValue="value"
              placeholder="Switch Account"
            >
            </Select>
          </div>
        </div>
        <router-view />
        <Toast position="bottom-right" group="br" />
        <Toast position="bottom-center" group="bc" />
      </div>
    </div>
  </div>
</template>

<script setup>
  import { useAuth0 } from "@auth0/auth0-vue"
  import {
    onMounted,
    watch,
    ref,
    inject,
    reactive,
    provide,
    computed
  } from "vue"
  import { useRoute } from "vue-router"
  import Dropdown from "primevue/dropdown"
  import { useUsers } from "@/store/modules/users"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import AccountApi from "@/api/account"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"
  import RolesApi from "@/api/roles"
  import { breakpointsTailwind, useBreakpoints } from "@vueuse/core"
  import AppMenu from "./AppMenu.vue"
  import CustomerApi from "@/api/customers"
  import { useToast } from "primevue/usetoast"
  import { envCheck } from "@/utils/envCheck"
  import { ABILITY_TOKEN } from "@casl/vue"
  import Payment from "../pages/Payment.vue"
  import { storeToRefs } from "pinia"

  const breakpoints = useBreakpoints(breakpointsTailwind)
  const smAndSmaller = breakpoints.isSmallerOrEqual("sm")
  const auth0 = useAuth0()
  const customerApi = new CustomerApi()

  import { useErrorHandler } from "@/store/modules/errorHandler"

  const usersStore = useUsers()
  const customerOrderStore = useCustomerOrder()

  const { cms } = storeToRefs(usersStore)

  const usersService = new UsersService()
  const userApi = new UserApi()
  const rolesApi = new RolesApi()

  const accountApi = new AccountApi()
  const toast = useToast()
  const visibleLeft = ref(false)
  const state = reactive({
    refreshKey: 0,
    showLogin: true,
    loadingUsers: false
  })

  const useRouteVar = useRoute()
  const $route = inject("$route")
  const $logoPath = inject("$logoPath")
  const $title = inject("$title")

  const $isObjectPopulated = inject("$isObjectPopulated")
  const $isPublic = inject("$isPublic") || useRouteVar.path.includes("/quoting")
  const $isPayment =
    inject("$isPayment") || useRouteVar.path.includes("/prices/payment")

  const $ability = inject(ABILITY_TOKEN)
  provide("$ability", $ability)

  const insertGoogleScript = () => {
    if (
      usersStore.integrations?.google_analytic_gtag_id?.enabled &&
      usersStore.integrations?.google_analytic_gtag_id?.general !== "" &&
      !isDev.value
    ) {
      console.log("inserting google script (AppLayout.vue)")
      const googleAdScript = document.createElement("script")
      googleAdScript.innerHTML = `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','${usersStore.integrations?.google_analytic_gtag_id?.general}');`

      window.document.body.appendChild(googleAdScript)
      const googleIframeScript = document.createElement("noscript")
      googleIframeScript.innerHTML = `<iframe src="https://www.googletagmanager.com/ns.html?id=${usersStore.integrations?.google_analytic_gtag_id?.general}" height="0" width="0" style="display:none;visibility:hidden"></iframe>`
      window.document.body.appendChild(googleIframeScript)
    }
  }

  const insertGoogleScriptPayments = () => {
    if (
      usersStore.integrations?.google_analytic_gtag_id?.enabled &&
      usersStore.integrations?.google_analytic_gtag_id?.payments !== "" &&
      !isDev.value
    ) {
      console.log(
        "inserting google script (AppLayout.vue) ",
        usersStore.integrations?.google_analytic_gtag_id?.payments
      )

      const googleAdScript = document.createElement("script")
      const googleAdScript2 = document.createElement("script")

      googleAdScript.src = `https://www.googletagmanager.com/gtag/js?id=${usersStore.integrations?.google_analytic_gtag_id?.payments}`
      googleAdScript2.innerHTML = `window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', '${usersStore.integrations?.google_analytic_gtag_id?.payments}');`

      window.document.body.appendChild(googleAdScript)
      window.document.body.appendChild(googleAdScript2)
    }
  }

  onMounted(async () => {
    if ($isPublic || $isPayment) {
      return
    }

    if (usersStore.darkMode) {
      document.documentElement.classList.add("app-dark")
    } else {
      document.documentElement.classList.remove("app-dark")
    }
    console.log("auth0.isAuthenticated", auth0.isAuthenticated.value)

    await auth0.checkSession()
    if (!auth0.isAuthenticated.value && !$isPayment) {
      state.showLogin = true
      // await auth0.loginWithRedirect();
    }
  })
  const loadFeeTypes = async () => {
    let { data, error } = await customerApi.fetchFeeTypes()
    customerOrderStore.setFeeTypes(data.value)
  }
  const getUsers = async () => {
    state.loadingUsers = true
    const { data } = await userApi.getUsers()
    const mappedUsers = data.value
      .map((d) => usersService.dtoUser(d))
      .sort((a, b) =>
        a.first_name.toLowerCase().localeCompare(b.first_name.toLowerCase())
      )

    usersStore.setUsers(mappedUsers)
    state.loadingUsers = false
  }

  const filteredMappedUsers = ref([])

  const search = (event) => {
    setTimeout(() => {
      if (!event.query.trim().length) {
        filteredMappedUsers.value = [...mappedUsers]
      } else {
        filteredMappedUsers.value = usersStore.users
          ?.map((user) => {
            return {
              label: user.full_name,
              value: user.id
            }
          })
          .filter((el) => {
            return el.label.toLowerCase().startsWith(event.query.toLowerCase())
          })
      }
    }, 250)
  }

  const pullData = async () => {
    if ($isPublic || $isPayment) {
      return
    }

    const { data } = await accountApi.getAccount()
    const attributes = data.value.cms_attributes
    attributes.id = data.value.id
    usersStore.setCms(attributes)
    usersStore.setIntegrations(data.value.integrations)
    await loadFeeTypes()

    if (usersStore.roles.length === 0) {
      let { data } = await rolesApi.getRoles()
      usersStore.setRoles(data.value)
    }
  }

  const isDev = computed(() => {
    return envCheck()
  })

  const selectedUser = ref(null)
  const selectedAccount = reactive({
    id: null
  })

  const mappedUsers = computed(() => {
    return usersStore.users?.map((user) => {
      return {
        label: user.full_name,
        value: user.id
      }
    })
  })
  const errorHandler = useErrorHandler()

  const stopEmulating = async () => {
    usersStore.setIsEmulating(false)
    selectedUser.value = null
    await usersService.setCurrentUserFromAuthUser()
    usersService.updateAbility($ability)
  }
  watch(
    () => errorHandler.hasError,
    async (newVal) => {
      console.log(newVal)
      if (newVal) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: errorHandler.errorMessage,
          group: "br",
          life: 5000
        })
      }
      errorHandler.setError(false, "", 0)
    }
  )
  watch(
    () => selectedUser,
    async (user) => {
      if (user.value) {
        console.log("user", user.value.label)
        const { data } = await userApi.getUserById(user.value.value)
        usersStore.setCurrentUser(usersService.dtoUser(data.value))
        usersService.updateAbility($ability)
        usersStore.setIsEmulating(true)
      }
    },
    { immediate: true, deep: true }
  )

  watch(
    () => selectedAccount.id,
    async (newVal, oldValue) => {
      //
      if (oldValue != null) {
        state.loadingUsers = true
        await userApi.switchUser(usersStore.currentUser.id, newVal)
        await auth0.loginWithRedirect()
        state.loadingUsers = false
      }
    }
  )

  watch(
    () => auth0.isAuthenticated,
    async (newVal) => {
      if (newVal.value) {
        state.showLogin = false
      }
    },
    { immediate: true, deep: true }
  )

  const retry = ref(true)
  const retry_limit = ref(10)

  watch(
    async () => auth0.user.value,
    async (newVal) => {
      if (isDev.value) {
        if (retry.value && retry_limit.value > 0) {
          retry.value = false
          retry_limit.value -= 1
        } else {
          return
        }
      }

      const user = await newVal
      if (user && $isObjectPopulated(user)) {
        await pullData()
        await usersService.setCurrentUserFromAuthUser()
        usersService.updateAbility($ability)
        selectedAccount.id = usersStore.currentUser?.account_id
      } else {
        retry.value = true
      }
    },
    { immediate: true, deep: true }
  )

  watch(cms, (newVal, oldValue) => {
    if (usersStore.cms?.has_analytics) {
      insertGoogleScript()
      insertGoogleScriptPayments()
    }
  })
</script>

<style lang="scss" scoped>
  // @import '../assets/styles/layout.scss';
  .canada-color {
    width: 100%;
    background-color: lightcoral;
  }
</style>
