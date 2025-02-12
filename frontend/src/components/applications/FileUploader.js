import { markRaw } from "vue"

const FileUploader = markRaw({
  name: "FileUploader",
  props: {},
  template: `<FileUploader />`,
  setup() {
    return {}
  }
})

export default FileUploader
