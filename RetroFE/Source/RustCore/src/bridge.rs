// CXX Bridge - C++ ↔ Rust Interop
//
// This module defines the interface between C++ and Rust code.
// All functions exposed here are callable from C++.

#[cxx::bridge]
mod ffi {
    // Shared types that both C++ and Rust can use

    // Rust → C++ exposed functions
    extern "Rust" {
        /// Test function to verify Rust is callable from C++
        fn rust_test_connection() -> String;

        /// Get Rust core version
        fn get_rust_core_version() -> String;
    }

    // C++ → Rust exposed functions (placeholder for future use)
    unsafe extern "C++" {
        // include!("RetroFE/RustBridge.h");
        // Future: C++ functions that Rust needs to call
    }
}

/// Test function - Returns greeting from Rust
pub fn rust_test_connection() -> String {
    "Hello from Rust! Data modernization layer initialized.".to_string()
}

/// Returns the version of the Rust core module
pub fn get_rust_core_version() -> String {
    format!("RetroFE Rust Core v{}", env!("CARGO_PKG_VERSION"))
}
