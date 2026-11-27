#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod build_options;
mod titlebar;

fn main() {
    tauri::Builder::default()
        .on_page_load(|webview, payload| {
            if payload.event() != tauri::webview::PageLoadEvent::Finished {
                return;
            }

            if build_options::DISABLE_CONTEXT_MENU {
                let script = "document.addEventListener('contextmenu', (event) => { event.preventDefault(); }, true);";
                if let Err(error) = webview.eval(script) {
                    eprintln!("Failed to apply context-menu setting: {error}");
                }
            }

            if build_options::CUSTOM_TITLEBAR_ENABLED {
                let script = titlebar::build_script();
                if let Err(error) = webview.eval(&script) {
                    eprintln!("Failed to inject the custom title bar: {error}");
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("failed to run WebToExe application");
}
