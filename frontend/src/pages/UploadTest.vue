<template>
  <div>
    <h1>File Upload</h1>
    <input type="file" ref="fileInput" />
    <select ref="folderType">
      <option value="">Select and option...</option>
      <option value="dl_front">Front of Driver's license</option>
      <option value="dl_back">Back of Driver's license</option>
      <option value="cc_front">Front of Credit Card</option>
      <option value="cc_back">Back of Credit Card</option>
    </select>
    <label for="orderId">Order Id</label>
    <input type="text" id="orderId" ref="orderId" />
    <button @click="uploadFile">Upload</button>
  </div>
</template>

<script>
  import UploadApi from "@/api/upload.js" // Import the UploadApi class
  const uploadApi = new UploadApi()

  export default {
    methods: {
      async uploadFile() {
        const uploadApi = new UploadApi()

        try {
          // Get the selected file and content type from the input element
          const fileInput = this.$refs.fileInput
          const folderType = this.$refs.folderType.value
          const file = fileInput.files[0]
          const contentType = file.type // You can specify the content type here
          const orderId = this.$refs.orderId.value

          const fileReader = new FileReader()

          // Upload the file using the UploadApi class
          await uploadApi.sendToS3(
            file.name,
            file,
            contentType,
            folderType,
            orderId
          )

          // Handle success or display a success message
          console.log("File uploaded successfully!")
        } catch (error) {
          // Handle errors or display an error message
          console.error("Error:", error)
        } finally {
          this.$refs.fileInput = null
          this.$refs.folderType.value = ""
          this.$refs.orderId = ""
        }
      }
    }
  }
</script>
