import { accountMap } from "./src/utils/accountMap";

document.addEventListener("DOMContentLoaded", function () {
  const currentUrl = window.location.host;
  const accountData = accountMap[currentUrl];
  console.log("Account Data:", accountData);

  if (accountData && accountData.account_id) {
    document.title = accountData.title;
  }

  const faviconLink = document.createElement("link");
  faviconLink.setAttribute("rel", "icon");
  faviconLink.setAttribute("href", accountData.logo || "/default-favicon.png");
  document.head.appendChild(faviconLink);

  const appleFaviconLink = document.createElement("link");
  appleFaviconLink.setAttribute("rel", "apple-touch-icon");
  appleFaviconLink.setAttribute("href", accountData.logo || "/default-apple-icon.png");
  document.head.appendChild(appleFaviconLink);

  const hideAfterLoadEl = document.getElementById("hide-after-load");
  if (hideAfterLoadEl) {
    hideAfterLoadEl.style.display = "none";
  } else {
    console.warn("Element with ID 'hide-after-load' not found.");
  }

  if (accountData && accountData.theme) {
    const themeLink = document.createElement("link");
    themeLink.setAttribute("id", "theme-link");
    themeLink.setAttribute("rel", "stylesheet");
    themeLink.setAttribute("type", "text/css");
    themeLink.setAttribute("href", accountData.theme);
    document.head.appendChild(themeLink);
  }

  setupIcon();
});

function setupIcon() {
  const currentUrl = window.location.host;
  const accountData = accountMap[currentUrl];
  if (accountData && accountData.logo) {
    let logoEl = document.getElementById("hide-after-load");
    if (logoEl) {
      logoEl.setAttribute("href", accountData.logo);
    } else {
      console.warn("Element with ID 'hide-after-load' not found.");
    }
  } else {
    console.warn("Account data or logo not found for URL:", currentUrl);
  }
}
