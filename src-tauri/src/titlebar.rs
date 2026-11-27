pub fn build_script() -> String {
    include_str!("titlebar.js")
        .replace("__APP_NAME_BASE64__", crate::build_options::APP_NAME_BASE64)
        .replace("__APP_ICON_BASE64__", crate::build_options::APP_ICON_BASE64)
        .replace("__SHOW_MINIMIZE__", if crate::build_options::SHOW_MINIMIZE_BUTTON { "true" } else { "false" })
        .replace("__SHOW_MAXIMIZE__", if crate::build_options::SHOW_MAXIMIZE_BUTTON { "true" } else { "false" })
}
