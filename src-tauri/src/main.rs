#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod build_options;

fn main() {
    tauri::Builder::default()
        .on_page_load(|webview, payload| {
            if build_options::DISABLE_CONTEXT_MENU
                && payload.event() == tauri::webview::PageLoadEvent::Finished
            {
                let script = "document.addEventListener('contextmenu', (event) => { event.preventDefault(); }, true);";
                if let Err(error) = webview.eval(script) {
                    eprintln!("Failed to apply context-menu setting: {error}");
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("failed to run WebToExe application");
}
