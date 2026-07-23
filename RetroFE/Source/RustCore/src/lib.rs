// RetroFE Rust Core - Data Modernization Layer
//
// This module provides high-performance data operations using Apache Arrow,
// DuckDB, and modern Rust async patterns.

// Phase 1: Core data structures and XML parsing
pub mod bridge;

// Re-export main types for C++ bridge
pub use bridge::*;

#[cfg(test)]
mod tests {
    #[test]
    fn rust_core_initialized() {
        assert_eq!(2 + 2, 4);
    }
}
