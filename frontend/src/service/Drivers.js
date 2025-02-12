import { useHttp } from "@/composables/useHttp"
import { dfl } from "@/service/DateFormat"
import formatPhone from "@/utils/formatPhone"

export default class DriversService {
  dtoDriver(driver) {
    return Object.assign({}, driver, {
      display_phone_number: formatPhone(driver.phone_number),
      created_at: dfl(driver.created_at),
      modified_at: dfl(driver.modified_at)
    })
  }

  columnOrdering = [
    {
      field: "company_name",
      display: "Company Name",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "created_at",
      display: "Created At",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "modified_at",
      display: "Modified At",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "city",
      display: "City",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "state",
      display: "State",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "province",
      display: "Province",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "cost_per_mile",
      display: "Cost Per Mile",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "cost_per_100_miles",
      display: "Cost Per 100 Miles",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "display_phone_number",
      display: "Phone Number",
      sortable: true,
      style: "width: 160px"
    },
    {
      field: "email",
      display: "Email",
      sortable: true,
      style: "width: 160px"
    }
  ]
}
