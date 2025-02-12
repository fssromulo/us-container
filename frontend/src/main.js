import "primeicons/primeicons.css"
import "./assets/main.css"
import Aura from "@primevue/themes/aura"
import { definePreset } from "@primevue/themes"

import { createApp, reactive } from "vue"
import router from "./router"
import AppWrapper from "./AppWrapper.vue"
import { envCheck } from "./utils/envCheck"

// import App from './App.vue';

import PrimeVue from "primevue/config"
import AutoComplete from "primevue/autocomplete"
import Accordion from "primevue/accordion"
import AccordionHeader from "primevue/accordionheader"
import AccordionPanel from "primevue/accordionpanel"
import AccordionContent from "primevue/accordioncontent"

import Avatar from "primevue/avatar"
import Badge from "primevue/badge"
import BadgeDirective from "primevue/badgedirective"
import Button from "primevue/button"
import DatePicker from "primevue/datepicker"
import Card from "primevue/card"
import Checkbox from "primevue/checkbox"
import Chip from "primevue/chip"
import Chips from "primevue/chips"
import Column from "primevue/column"
import ConfirmDialog from "primevue/confirmdialog"
import ConfirmPopup from "primevue/confirmpopup"
import ConfirmationService from "primevue/confirmationservice"
import ContextMenu from "primevue/contextmenu"
import DataTable from "primevue/datatable"
import Row from "primevue/row"
import ColumnGroup from "primevue/columngroup"
import DataView from "primevue/dataview"
import Dialog from "primevue/dialog"
import Divider from "primevue/divider"
import Fieldset from "primevue/fieldset"
import FileUpload from "primevue/fileupload"
import Image from "primevue/image"
import Inplace from "primevue/inplace"
import InputMask from "primevue/inputmask"
import InputNumber from "primevue/inputnumber"
import ToggleSwitch from "primevue/toggleswitch"
import InputText from "primevue/inputtext"
import FloatLabel from "primevue/floatlabel"
import Knob from "primevue/knob"
import Listbox from "primevue/listbox"
import Menu from "primevue/menu"
import Menubar from "primevue/menubar"
import Message from "primevue/message"
import MultiSelect from "primevue/multiselect"
import OrderList from "primevue/orderlist"
import OrganizationChart from "primevue/organizationchart"
import Paginator from "primevue/paginator"
import Panel from "primevue/panel"
import Popover from "primevue/popover"
import PanelMenu from "primevue/panelmenu"
import Password from "primevue/password"
import PickList from "primevue/picklist"
import ProgressBar from "primevue/progressbar"
import Rating from "primevue/rating"
import RadioButton from "primevue/radiobutton"
import Ripple from "primevue/ripple"
import SelectButton from "primevue/selectbutton"
import ScrollPanel from "primevue/scrollpanel"
import ScrollTop from "primevue/scrolltop"
import Slider from "primevue/slider"
import Drawer from "primevue/drawer"
import Skeleton from "primevue/skeleton"
import SplitButton from "primevue/splitbutton"
import Splitter from "primevue/splitter"
import SplitterPanel from "primevue/splitterpanel"
import Steps from "primevue/steps"
import StyleClass from "primevue/styleclass"
import TabMenu from "primevue/tabmenu"
import Tag from "primevue/tag"
import TieredMenu from "primevue/tieredmenu"
import Textarea from "primevue/textarea"
import Timeline from "primevue/timeline"
import Toast from "primevue/toast"
import ToastService from "primevue/toastservice"
import Toolbar from "primevue/toolbar"
import TabView from "primevue/tabview"
import TabPanel from "primevue/tabpanel"
import Tooltip from "primevue/tooltip"
import ToggleButton from "primevue/togglebutton"
import Tree from "primevue/tree"
import TreeSelect from "primevue/treeselect"
import TreeTable from "primevue/treetable"
import ProgressSpinner from "primevue/progressspinner"
import Carousel from "primevue/carousel"
import OverlayBadge from "primevue/overlaybadge"
import Chart from "primevue/chart"
import { auth0 } from "@/service/authService"
import { DateTime } from "luxon"

import formatCurrency from "@/utils/formatCurrency"
import isObjectPopulated from "@/utils/isObjectPopulated"
import arrayMove from "@/utils/arrayMove"
import removeUnusedProps from "@/utils/removeUnusedProps"
import formatPhone from "@/utils/formatPhone"
import { abilitiesPlugin } from "@casl/vue"
import { Ability } from "@casl/ability"

import { createPinia, PiniaVuePlugin } from "pinia"

import { plugin, defaultConfig } from "@formkit/vue"
import { primeInputs } from "@sfxcode/formkit-primevue"
import { accountMap } from "./utils/accountMap"

import { Settings } from "luxon"
import Paperizer from "paperizer"
import Select from "primevue/select"
Settings.defaultZoneName = "America/Denver"
import posthog from "posthog-js"

const app = createApp(AppWrapper)

export const $DateTime = DateTime
if (!envCheck()) {
  posthog.init("phc_ETgVABOqucxBsI3KZv9c1FyVw28LMydhAswrqVaxr8p", {
    api_host: "https://us.posthog.com"
  })
}
app.use(PiniaVuePlugin)
app.use(createPinia())
app.use(router)
app.provide("$route", router)
app.provide("$DateTime", $DateTime)
app.provide("$isObjectPopulated", isObjectPopulated)
app.provide("$formatCurrency", formatCurrency)
app.provide("$arrayMove", arrayMove)
app.provide("$removeUnusedProps", removeUnusedProps)
app.provide("$formatPhone", formatPhone)

app.provide("$isPublic", accountMap[window.location.host].isPublic)

app.provide("$title", accountMap[window.location.host].title)
app.provide("$logoPath", accountMap[window.location.host].logo)
app.provide("$isPayment", accountMap[window.location.host].isPayment)

app.use(abilitiesPlugin, new Ability())

app.use(
  plugin,
  defaultConfig({
    // Define the active locale
    locale: "en",
    inputs: primeInputs
  })
)
// app.use(store);

app.use(auth0)
app.use(Paperizer)
const GeneralPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: "#ffffff",
      100: "#cacfdc",
      200: "#a1a9c1",
      300: "#7784a6",
      400: "#4e5e8a",
      500: "#24386f",
      600: "#1f305e",
      700: "#19274e",
      800: "#141f3d",
      900: "#0e162c",
      950: "{blue.950}"
    },
    colorScheme: {
      light: {
        surface: {
          0: "#ffffff",
          50: "#fafafa",
          100: "#f5f5f5",
          200: "#eeeeee",
          300: "#e0e0e0",
          400: "#bdbdbd",
          500: "#9e9e9e",
          600: "#757575",
          700: "#616161",
          800: "#424242",
          900: "#212121",
          950: "#09090b"
        }
      },
      dark: {
        surface: {
          0: "#fff",
          50: "#1d2530",
          100: "#363d47",
          200: "#4f565e",
          300: "#686e75",
          400: "#82868c",
          500: "#9b9ea3",
          600: "#b4b6ba",
          700: "#0b213f",
          800: "#0b213f",
          900: "#040d19",
          950: "#020617"
        }
      }
    }
  },
  components: {
    selectButton: {
      invalid: {
        border: {
          color: "#0b213f"
        }
      }
    }
  }
})

app.use(PrimeVue, {
  ripple: true,
  theme: {
    preset: GeneralPreset,
    options: {
      darkModeSelector: ".app-dark",
      prefix: "p",
      cssLayer: {
        name: "tailwind-base",
        order: "tailwind-utilities, tailwind-base, primevue"
      }
    }
  }
})
app.use(ConfirmationService)
app.use(ToastService)

app.directive("tooltip", Tooltip)
app.directive("ripple", Ripple)
app.directive("badge", BadgeDirective)
app.directive("styleclass", StyleClass)

app.component("ProgressSpinner", ProgressSpinner)
app.component("Carousel", Carousel)
app.component("OverlayBadge", OverlayBadge)
app.component("Accordion", Accordion)
app.component("AccordionHeader", AccordionHeader)
app.component("AccordionPanel", AccordionPanel)
app.component("AccordionContent", AccordionContent)
app.component("AutoComplete", AutoComplete)
app.component("Avatar", Avatar)
app.component("Badge", Badge)
app.component("Button", Button)
app.component("DatePicker", DatePicker)
app.component("Card", Card)
app.component("Checkbox", Checkbox)
app.component("Chip", Chip)
app.component("Chips", Chips)
app.component("Column", Column)
app.component("ConfirmDialog", ConfirmDialog)
app.component("ConfirmPopup", ConfirmPopup)
app.component("ContextMenu", ContextMenu)
app.component("DataTable", DataTable)
app.component("Row", Row)
app.component("ColumnGroup", ColumnGroup)
app.component("DataView", DataView)
app.component("Dialog", Dialog)
app.component("Divider", Divider)
app.component("Fieldset", Fieldset)
app.component("FileUpload", FileUpload)
app.component("Image", Image)
app.component("Inplace", Inplace)
app.component("InputMask", InputMask)
app.component("InputNumber", InputNumber)
app.component("ToggleSwitch", ToggleSwitch)
app.component("InputText", InputText)
app.component("FloatLabel", FloatLabel)
app.component("Knob", Knob)
app.component("Listbox", Listbox)
app.component("Menu", Menu)
app.component("Menubar", Menubar)
app.component("Message", Message)
app.component("MultiSelect", MultiSelect)
app.component("OrderList", OrderList)
app.component("OrganizationChart", OrganizationChart)
app.component("Paginator", Paginator)
app.component("Panel", Panel)
app.component("PanelMenu", PanelMenu)
app.component("Password", Password)
app.component("PickList", PickList)
app.component("ProgressBar", ProgressBar)
app.component("RadioButton", RadioButton)
app.component("Rating", Rating)
app.component("SelectButton", SelectButton)
app.component("ScrollPanel", ScrollPanel)
app.component("ScrollTop", ScrollTop)
app.component("Slider", Slider)
app.component("Drawer", Drawer)
app.component("Skeleton", Skeleton)
app.component("SplitButton", SplitButton)
app.component("Splitter", Splitter)
app.component("SplitterPanel", SplitterPanel)
app.component("Steps", Steps)
app.component("TabMenu", TabMenu)
app.component("TabView", TabView)
app.component("TabPanel", TabPanel)
app.component("Tag", Tag)
app.component("Textarea", Textarea)
app.component("TieredMenu", TieredMenu)
app.component("Timeline", Timeline)
app.component("Toast", Toast)
app.component("Toolbar", Toolbar)
app.component("ToggleButton", ToggleButton)
app.component("Tree", Tree)
app.component("TreeSelect", TreeSelect)
app.component("TreeTable", TreeTable)
app.component("Select", Select)
app.component("Popover", Popover)
app.component("Chart", Chart).mount("#app")
