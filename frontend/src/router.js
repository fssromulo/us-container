import { createRouter, createWebHashHistory } from "vue-router"
import { accountMap } from "./utils/accountMap"
import { ABILITY_TOKEN } from "@casl/vue"
import { useUsers } from "./store/modules/users"

import { inject } from "vue"

let redirectPath = "/invoices?status=invoiced"
let path = "/"

if (accountMap[window.location.host]?.account_id === 1) {
  if (accountMap[window.location.host].isPublic) {
    redirectPath = "/quotes"
  }

  if (window.location.host === "quote.usacontainers.co") {
    redirectPath = ""
    path = "/:orderId"
  }
} else {
  if (accountMap[window.location.host].isPublic) {
    redirectPath = "/quotes"
  }
}

const routes = [
  {
    path: path,
    name: "home",
    redirect: redirectPath,
    component: () => import("@/layout/AppLayout.vue"),
    children: [
      {
        path: "/application",
        name: "Application",
        component: () => import("@/pages/Application.vue")
      },
      {
        path: "/quotes",
        name: "Quote",
        component: () => import("@/pages/GenerateQuote.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/quoting",
        name: "CanadaQuoting",
        component: () => import("@/pages/GenerateQuote.vue")
      },
      {
        path: "/Reporting",
        name: "Reporting",
        component: () => import("@/pages/Reporting.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/receipt/:id",
        name: "receipt_with_id",
        component: () => import("@/pages/Receipt.vue")
      },
      {
        path: "/inventory/:id",
        name: "inventory_with_id",
        component: () => import("@/pages/Inventory.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/inventory",
        name: "inventory",
        component: () => import("@/pages/Inventory.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/invoices/:id",
        name: "invoices_with_id",
        component: () => import("@/pages/Invoices.vue")
      },
      {
        path: "/invoices",
        name: "invoices",
        component: () => import("@/pages/Invoices.vue")
      },
      {
        path: "/pricing",
        name: "pricing",
        component: () => import("@/pages/Pricing.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/drivers",
        name: "drivers",
        component: () => import("@/pages/Drivers.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/prices",
        name: "prices",
        component: () => import("@/pages/Pricing.vue")
      },
      {
        path: "/prices/payment/:orderId",
        name: "canada_payment_page",
        component: () => import("@/pages/Payment.vue"),
        props: true
      },
      {
        path: "/commission",
        name: "commission",
        component: () => import("@/pages/Commission.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/settings",
        name: "settings",
        component: () => import("@/pages/Settings.vue")
      },
      {
        path: "/users",
        name: "users",
        component: () => import("@/pages/Users.vue"),
        meta: { requiresPermission: true }
      },
      {
        path: "/payment/:orderId/",
        name: "payment",
        component: () => import("@/pages/Payment.vue"),
        props: true
      },
      {
        path: "/rental_invoice/:orderId/:rentPeriodId",
        name: "rental_invoice",
        component: () =>
          import("@/components/invoicing/payment/RentalInvoice.vue"),
        props: true
      },
      {
        path: "/driver/customerpayment/:orderId/",
        name: "driverpayment",
        component: () => import("@/pages/DriverPayment.vue"),
        props: true
      },
      {
        path: "/upload",
        name: "upload",
        component: () => import("@/pages/UploadTest.vue")
      }
    ]
  }
]

if (
  accountMap[window.location.host].account_id == 2 &&
  accountMap[window.location.host].isPublic
) {
  routes[0].children.push({
    path: "/:orderId",
    name: "payment",
    component: () => import("@/pages/Payment.vue"),
    props: true
  })
}

if (accountMap[window.location.host].account_id == 1) {
  routes[0].children.push({
    path: "/contracts_pay_on_delivery/:orderId",
    name: "contracts_pay_on_delivery",
    component: () => import("@/pages/ContractsPayOnDelivery.vue"),
    redirect: "",
    props: true
  })
  routes[0].children.push({
    path: "/signed_pod_contract/:orderId",
    name: "signed_pod_contract",
    component: () => import("@/pages/SignedPodContract.vue"),
    redirect: "",
    props: true
  })

  routes[0].children.push({
    path: "/rental_contract/:orderId",
    name: "rental_contract",
    component: () => import("@/pages/RentalContract.vue"),
    redirect: "",
    props: true
  })
  routes[0].children.push({
    path: "/finished_signing",
    name: "finished_signing",
    component: () => import("@/pages/FinishedSigningRental.vue"),
    redirect: "",
    props: true
  })
}

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const $ability = inject(ABILITY_TOKEN)
  const $isPublic = inject("$isPublic")
  const userStore = useUsers()

  if (to.matched.some((record) => record.meta.requiresPermission)) {
    if (
      to.path == "/quotes" &&
      ($ability.can("read", "navigation-quotes") || $isPublic)
    ) {
      next()
    } else if (
      to.path.startsWith("/inventory") &&
      $ability.can("read", "navigation-inventory")
    ) {
      next()
    } else if (
      to.path == "/reports" &&
      $ability.can("read", "navigation-reports")
    ) {
      next()
    } else if (
      to.path == "/pricing" &&
      $ability.can("read", "navigation-products")
    ) {
      next()
    } else if (to.path == "/drivers" && $ability.can("attach", "driver")) {
      next()
    } else if (
      to.path == "/commission" &&
      $ability.can("read", "navigation-personal_commissions") &&
      userStore.cms?.feature_flags?.commmissions_enabled
    ) {
      next()
    } else if (
      to.path == "/guide" &&
      $ability.can("read", "navigation-agent_guide") &&
      userStore.cms?.feature_flags?.commmissions_enabled
    ) {
      next()
    } else if (to.path == "/settings") {
      next()
    } else if (
      to.path == "/users" &&
      $ability.can("read", "navigation-users")
    ) {
      next()
    } else if (to.path == "/reporting" && $ability.can("read", "reports")) {
      next()
    } else {
      next({
        path: "/invoices"
      })
    }
  } else {
    next()
  }
})

export default router
