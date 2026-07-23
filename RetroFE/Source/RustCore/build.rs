// Build script for CXX bridge code generation
//
// This generates the C++ header files that allow C++ code to call Rust functions

fn main() {
    cxx_build::bridge("src/bridge.rs")
        .flag_if_supported("-std=c++14")
        .compile("retrofe-core");

    println!("cargo:rerun-if-changed=src/bridge.rs");
    println!("cargo:rerun-if-changed=src/lib.rs");
}
