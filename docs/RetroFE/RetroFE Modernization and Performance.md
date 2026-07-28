# **Architectural Evolution of RetroFE: A Blueprint for the Next-Generation Gaming Frontend in 2026**

## **1\. Introduction: The Imperative for Architectural Modernization**

The domain of retro gaming frontends has transitioned from simple file launchers to complex, metadata-rich digital museums. As we navigate the landscape of 2026, the expectations for a "modern" frontend have been fundamentally reset by market leaders such as LaunchBox and open-source innovators. Users no longer accept static lists; they demand dynamic, fluid interfaces capable of managing tens of thousands of ROMs, filtering by granular metadata instantly, and rendering rich media at high frame rates on modest hardware.

For a custom fork of RetroFE to claim the "front of gaming frontend development," it must address the systemic limitations of its legacy architecture. The current reliance on XML for data storage—specifically the linear parsing of hyperlist.xml—represents a significant bottleneck in scalability and responsiveness. Furthermore, the media playback infrastructure, traditionally reliant on GStreamer or basic VLC implementations, fails to provide the seamless, frame-perfect integration required for the immersive "video-first" themes that define modern aesthetics.

This report outlines a comprehensive architectural strategy to "10x" the capabilities of RetroFE. It proposes a shift from a pure C++ codebase to a hybrid system leveraging **Rust** for core safety and concurrency, **Apache Arrow** and **DuckDB** for a revolutionary data layer, and **libmpv** for embedded media rendering. This analysis focuses specifically on the Windows ecosystem, aiming to optimize performance for lower-end hardware while delivering feature parity with premium competitors like LaunchBox.

### **1.1 The Legacy Bottleneck: XML and C++**

The traditional RetroFE architecture, centered on C++ and XML, faces diminishing returns. XML is inherently hierarchical and verbose, requiring parsing strategies that scale linearly with dataset size. As collections grow—often exceeding 100,000 items when combining full sets of diverse systems like the Atari 2600, MAME, and modern platforms—the startup time and memory footprint of an XML-based DOM (Document Object Model) become prohibitive.

In contrast, modern applications operate on data-oriented design principles. The user’s request to "10x the hyperlist" implies not just increasing the number of supported items, but exponentially increasing the *density* of metadata per item. A typical hyperlist.xml entry might contain a name, description, and year. A modern schema must support publisher, developer, community ratings, play counts, specific input types (e.g., lightgun vs. controller), region codes, and user-defined tags.1 Managing this expanded schema in XML would render the application sluggish on the targeted low-end hardware.

### **1.2 The Competitor Landscape: LaunchBox and Beyond**

LaunchBox has established dominance through features like "Smart Playlists," cloud synchronization of play data, and deeply integrated metadata scraping.2 However, LaunchBox is built on the.NET framework (C\#), which entails the overhead of a managed runtime and garbage collection. This creates an opening for a native, compiled solution. By utilizing Rust, a RetroFE fork can theoretically achieve lower memory usage and more consistent frame times than.NET-based competitors, provided the architecture is designed to minimize resource contention.3

The proposed roadmap does not merely play catch-up; it leapfrogs current standards by adopting **Apache Arrow**. While LaunchBox relies on its own XML/Database hybrid 1, Arrow provides a standardized, zero-copy memory format used in high-performance data science. Adopting this allows RetroFE to perform complex queries—such as "Show all unplayed RPGs from 1995-1999 supported by 2 players"—in microseconds rather than seconds.

## ---

**2\. Core Architecture: The Transition to Rust**

The strategic integration of Rust into the RetroFE codebase is the primary vehicle for achieving the requested modernization. Rust offers memory safety guarantees without a garbage collector, making it uniquely suited for the high-concurrency, low-latency requirements of a gaming frontend.3

### **2.1 The Case for Rust in Frontend Development**

Gaming frontends function similarly to game engines: they possess a main loop that must render frames within a 16.6ms budget (for 60fps) while simultaneously handling asynchronous tasks such as loading images, querying databases, and polling input. In C++, managing the lifetimes of these asynchronous resources is a frequent source of race conditions and crashes. Rust’s ownership model prevents these errors at compile time, ensuring that the "Loading" thread cannot invalidate the memory used by the "Rendering" thread.4

Furthermore, the Rust ecosystem in 2026 has matured to offer best-in-class libraries for the components critical to this project: **Tokio** for asynchronous I/O, **WGPU** for modern graphics abstraction, and **Arrow-rs** for data handling.5 Transitioning core components to Rust allows the developer to leverage these battle-tested libraries rather than maintaining custom C++ implementations.

### **2.2 Interoperability Strategy: Extending C++ with CXX**

Given that RetroFE is an existing C++ codebase, a complete rewrite is often impractical. The optimal path is a hybrid architecture where Rust "modules" replace aging C++ subsystems one by one. The **CXX** library is the recommended tool for this interoperability, superior to manual extern "C" bindings or simple bindgen usage.7

**CXX** generates a bridge that allows C++ and Rust to call each other’s functions safely. Unlike bindgen, which essentially exposes unsafe C pointers, CXX checks types across the language boundary. This is critical for the "Data Engine" replacement. The C++ UI layer can request a view of the data (e.g., "Get Wheel Items"), and the Rust engine can return a smart pointer to the data without risking memory corruption.8

| Component | Current State (C++) | Proposed State (Rust) | Migration Method |
| :---- | :---- | :---- | :---- |
| **Data Storage** | hyperlist.xml / TinyXML | Apache Arrow / DuckDB | Rust library exposed via CXX |
| **Asset Loading** | SDL\_Image (Blocking/Threaded) | image-rs \+ Tokio (Async) | Rust Async Task Pool |
| **Input Handling** | SDL2 Event Loop | winit / gilrs | Keep C++ initially, migrate later |
| **Rendering** | SDL2 / OpenGL | wgpu (DX12/Vulkan) | Replace rendering backend last |

### **2.3 Choosing a Rust GUI Framework**

The query specifically mentions looking at Rust for core components. While **Tauri** is popular for desktop apps, it relies on a webview (HTML/JS), which incurs high memory overhead—counter to the goal of optimizing for low-end machines.9 For a gaming frontend, a native rendering approach is superior.

**Iced** or a custom renderer built on **wgpu** is the architectural recommendation. **Iced** employs the Elm architecture (Model-View-Update), which maps perfectly to a frontend's state requirements (e.g., State \= Selected Game, View \= Box Art \+ Text). More importantly, wgpu automatically selects the most performant graphics backend for the Windows machine—running on DirectX 12 for modern GPUs or falling back to Vulkan/DX11 for older integrated graphics. This abstraction simplifies the burden of supporting diverse low-end hardware configurations.10

## ---

**3\. Data Revolution: Apache Arrow & DuckDB**

The user asks, "Is XML even the way still?" The definitive answer for high-performance applications in 2026 is **no**. XML is a serialization format, not a queryable data structure. To "10x the hyperlist"—scaling from hundreds to tens of thousands of games with rich metadata—the architecture must shift to **Columnar Data Storage**.

### **3.1 The Performance Deficit of XML**

In the current RetroFE hyperlist.xml, data is stored row-by-row. To find all games in the "Action" genre, the CPU must parse the entire file, traversing every node for every game. This causes frequent CPU cache misses because relevant data (Genre) is interleaved with irrelevant data (Description, CloneOf, Manufacturer).

For an Atari 2600 set (approx. 500-700 games), XML is passable. For a full MAME set (30,000+ entries) or a combined multi-system library (100,000+ entries), XML parsing introduces multi-second delays on startup and stuttering during "search" operations.

### **3.2 The Solution: Apache Arrow**

**Apache Arrow** is an in-memory format that organizes data by column rather than by row.

* **Columnar Efficiency:** All "Year" values are stored in a contiguous block of memory. To filter by "Year \> 1990", the CPU can load this block into its cache and use SIMD (Single Instruction, Multiple Data) instructions to process multiple years per clock cycle.12  
* **Zero-Copy Serialization:** Arrow data on disk (using the IPC format) is identical to Arrow data in memory. This means the application can "memory map" the file, making it available instantly without CPU-intensive parsing.13

### **3.3 DuckDB: The Query Engine**

While Arrow provides the memory layout, **DuckDB** provides the logic. DuckDB is an embedded SQL OLAP (Online Analytical Processing) database designed to query Arrow data directly.

* **Integration:** DuckDB can run SQL queries against Arrow buffers held in the Rust application's memory without copying the data.15  
* **Capability:** This enables the "Smart Features" requested. A user can create a dynamic collection defined by: SELECT \* FROM games WHERE rating \>= 4 AND last\_played \< '2025-01-01'. DuckDB executes this query in milliseconds, even over massive datasets.

This architecture decouples the *view* of the data from the *storage* of the data. The frontend no longer iterates through a list; it simply requests a "view" from the DuckDB engine, which returns a lightweight pointer to the relevant rows.

## ---

**4\. Metadata Expansion: The "10x" HyperList**

To fulfill the request of "10x-ing" the hyperlist, we must move beyond the basic fields (Name, Description, Year) found in the Atari XML. We will adopt and extend the **Video Game Metadata Schema (VGMS)**, a comprehensive standard for describing interactive media.16

### **4.1 Schema Definition for 2026**

The new data structure (defined in Arrow) should include the following categories to support modern frontend features.

#### **4.1.1 Core Taxonomy**

* **game\_id (UUID):** A unique identifier is essential for tracking play history across file renames.  
* **input\_type (Dictionary):** Crucial for filtering. Values: *Gamepad, Keyboard, Mouse, Lightgun, Steering Wheel, Flight Stick*. This allows users to create a "Lightgun Games" wheel automatically.  
* **pacing (Dictionary):** Values: *Real-time, Turn-based*. Useful for distinguishing RPG sub-genres.  
* **perspective (Dictionary):** Values: *Top-Down, Side-Scrolling, Isometric, First-Person, Third-Person*.  
* **coop\_type (Dictionary):** Values: *Couch Co-op, LAN, Online, Split-Screen, Simultaneous, Alternating*. This enables the specific query: "Show me 2-player simultaneous co-op games."

#### **4.1.2 Dynamic Tags (The "10x" Feature)**

The most significant addition is the **Tags** system. In Arrow, this is implemented as a List\<Utf8\> column. This allows an arbitrary number of descriptors per game without altering the schema structure.18

* **Usage:** Tags can cover themes (*Cyberpunk, Steampunk, Noir*), technical features (*Save States Supported, Netplay, RetroAchievements*), or user-specific markers (*Beaten, Backlog, Favorite*).  
* **Auto-Tagging:** The Rust core can integrate logic to auto-tag games. For example, scanning the ROM file extension or hash can automatically apply tags like "Multi-Disc" (if .m3u) or "Hack" (if matching known ROM hacks).

#### **4.1.3 Community & Social Metrics**

LaunchBox leverages community data. RetroFE should include fields for:

* **community\_rating (Float32):** Aggregated score from sources like LaunchBox DB or ScreenScraper.  
* **community\_play\_count (UInt64):** Popularity metric.  
* **retroachievements\_id (UInt32):** Link to the RetroAchievements API to show live progress bars on the menu.19

### **4.2 Handling the "Atari HyperList" Migration**

The user attached an Atari XML. To facilitate the transition, a migration utility is required. This tool, written in Rust, would:

1. Parse the legacy hyperlist.xml.  
2. Map existing fields to the new Arrow schema.  
3. Enrich the data by querying an API (like ScreenScraper) using the game name or ROM hash to fill the new "10x" fields (Developer, Publisher, Rating, Tags).  
4. Write the result to a .arrow file.  
   This ensures the user's existing setup works immediately while unlocking the new capabilities.

## ---

**5\. Dynamic Faceting and "Smart Playlists"**

The user specifically requested "menu wheels for genre, year, etc." In the legacy architecture, these required separate, manually curated XML files. In the new Data-Oriented architecture, these are **Dynamic Facets**.

### **5.1 Dynamic Query Logic**

Faceting is the process of grouping data by a specific attribute. With DuckDB, creating a "Genre Wheel" is a live aggregation query:  
SELECT genre, COUNT(\*) as count FROM games GROUP BY genre ORDER BY genre  
This query runs instantly. The Rust UI layer iterates over the results to generate the wheel items. This means if a user adds a new game with the genre "Space Opera," the "Space Opera" wheel item appears automatically without manual XML editing.20

### **5.2 Smart Playlists**

Smart Playlists are saved query definitions. Instead of a static list of games, the frontend stores a JSON definition of the filter logic.

* **Structure:**  
  JSON  
  {  
    "name": "90s Capcom Fighters",  
    "filters": \[  
      { "field": "genre", "operator": "contains", "value": "Fighting" },  
      { "field": "developer", "operator": "eq", "value": "Capcom" },  
      { "field": "year", "min": 1990, "max": 1999 }  
    \],  
    "sort\_by": "release\_date"  
  }

* **Implementation:** When the user selects this playlist, the system translates the JSON into a SQL WHERE clause and executes it against the Arrow table.  
* **Advantage:** This supports the user's request for "speed" and "10x updates." A playlist of 1,000 games takes virtually zero memory to store (just the rule definition), and the content is always up-to-date with the library.21

## ---

**6\. Rendering Pipeline: Optimization for Low-End Machines**

To perform well on "lower end machines" (e.g., integrated graphics), the frontend cannot afford to be wasteful. Modern "rich" themes with 4K assets can easily saturate the VRAM of a budget GPU.

### **6.1 Virtualized List Rendering**

A critical optimization is **UI Virtualization** (also known as Windowing).

* **The Problem:** Loading 1,000 game logos into a scrollable list normally requires creating 1,000 UI widgets. This consumes massive CPU time for layout calculation and RAM for state.22  
* **The Solution:** The renderer only creates widgets for the items currently visible on screen (plus a small buffer). If the screen shows 10 games, only \~15 widgets exist in memory.  
* **Mechanism:** As the user scrolls down, the widget that scrolls off the top is moved to the bottom, and its data (text, image texture) is swapped to represent the new game. This keeps the rendering cost constant (O(1)) regardless of whether the list has 100 or 100,000 items.23

### **6.2 Texture Streaming and VRAM Budgeting**

Low-end machines often have shared system/video memory. Loading high-res assets blindly causes paging to disk, resulting in severe stutter.

* **VRAM Budget:** The system should define a strict budget (e.g., 512MB).  
* **Streaming System:**  
  1. **Request:** When a game enters the viewport, the UI requests its box art.  
  2. **Check:** Is the texture in the LRU (Least Recently Used) cache? If yes, use it.  
  3. **Load:** If no, queue a load task on a background thread. Return a lightweight "Loading" placeholder texture immediately.  
  4. **Upload:** Once the background thread decodes the image, upload it to the GPU and swap the placeholder.  
  5. **Evict:** If the budget is exceeded, unload the oldest textures from the cache.25

### **6.3 Texture Atlasing for UI Elements**

To reduce draw calls, small static UI elements (rating stars, system icons, controller glyphs) should be packed into a single **Texture Atlas**. This allows the GPU to draw the entire UI overlay in a single pass, rather than binding a new texture for every icon. This is particularly effective on older GPUs where state changes (binding textures) are CPU-expensive.27

## ---

**7\. Media Engine: Libmpv Integration**

The user replaced GStreamer with VLC but asks for the "front of development." In 2026, **libmpv** is widely regarded as the superior choice for embedded usage over LibVLC.

### **7.1 MPV vs. VLC for Frontends**

* **Architecture:** LibVLC is designed primarily as a standalone player. Embedding it often involves "hacks" like rendering to a separate OS window (HWND) overlaid on the app, which prevents true UI layering (e.g., transparent menus *over* the video).29  
* **Rendering Control:** **Libmpv** offers a sophisticated Render API that allows the application to control exactly how the video frame is composited. It can output directly to an OpenGL texture or Vulkan image.  
  * *Benefit:* This enables "zero-copy" rendering where the decoded video frame stays on the GPU and is mapped to a UI surface. This is critical for the user's "low-end machine" requirement, as it avoids moving 4K video data between CPU and GPU RAM.

### **7.2 Integration with WGPU**

In a Rust/WGPU environment, libmpv can be integrated via the mpv\_render\_context\_report\_swap API. The application creates a texture in WGPU, passes the handle to MPV, and MPV renders the video frame into it. This texture is then drawn by the UI toolkit (Iced) like any other image. This seamless integration allows for complex theme effects, such as blurring the video background or applying shaders, which are impossible with a standard VLC overlay.

## ---

**8\. Performance Optimization on Windows**

Windows presents specific challenges and opportunities for optimization.

### **8.1 Threading Model**

To ensure the UI never freezes (a common issue in XML-heavy frontends):

* **Main Thread:** Handles **only** Input processing and GPU command submission. It should execute in \<16ms.  
* **Tokio Runtime:** A pool of background threads handles everything else: database queries (DuckDB), file I/O, image decoding, and scraping.  
* **Priority Management:** Image decoding threads should run at a lower priority than the main thread to prevent CPU starvation on dual-core low-end machines.

### **8.2 Windows-Specific APIs**

* **DirectStorage (Future Proofing):** While currently for NVMe SSDs, DirectStorage principles (bypassing CPU for file I/O) are entering general Windows APIs. Using Rust's async I/O positions the engine to take advantage of these OS-level improvements.  
* **Power Management:** On laptops/handhelds (like Windows gaming handhelds), the engine should cap the frame rate when idle or when the window is unfocused to save battery, a feature often overlooked in retro frontends.31

## ---

**9\. Future Features: Cloud and Social Integration**

Looking at LaunchBox's trajectory, the "front of development" includes connectivity.

### **9.1 RetroAchievements Integration**

The schema supports retroachievements\_id. The Rust core can query the RetroAchievements API to fetch the user's progress. This allows for a "Recently Earned Achievements" ticker on the dashboard or a "Mastered Games" filter—features that dramatically increase user engagement.2

### **9.2 Cloud Sync via Arrow**

Because the entire database is a single .arrow or .parquet file (or a folder of them), "Cloud Sync" becomes trivial. Syncing this single file via OneDrive or Dropbox allows the user to carry their play history, ratings, and smart playlists between their main PC and their arcade cabinet without complex database replication setups.

## ---

**10\. Conclusion and Roadmap**

To bring RetroFE to the forefront of development in 2026 requires a fundamental pivot from "Configurable Launcher" to "High-Performance Gaming Database."

**Summary of Recommendations:**

1. **Architecture:** Adopt a **Hybrid C++/Rust** model initially, utilizing **CXX** to safely bridge the legacy shell with a new high-performance core.  
2. **Data:** Abandon XML for **Apache Arrow** and **DuckDB**. This enables the requested "10x" scale, instant filtering, and smart playlists.  
3. **Metadata:** Implement the **VGMS** schema with a flexible **Tagging** system to support rich filtering (Genre, Year, Input Type, etc.).  
4. **Media:** Transition from VLC to **libmpv** using the Render API for seamless, hardware-accelerated integration into the UI.  
5. **Optimization:** Implement **UI Virtualization** and **Texture Streaming** with strict VRAM budgeting to ensure 60fps performance on low-end Windows hardware.

By executing this roadmap, the custom RetroFE build will not only match the capabilities of LaunchBox but exceed them in performance and architectural elegance, securing its place as a next-generation frontend.

### **Comparison Table: Legacy RetroFE vs. Proposed Architecture**

| Feature | Legacy RetroFE (Current) | Proposed Architecture (2026) | User Benefit |
| :---- | :---- | :---- | :---- |
| **Data Format** | XML (HyperList) | Apache Arrow / Parquet | "10x" capacity, instant load times. |
| **Query Engine** | Linear Iteration (C++) | DuckDB (SQL on Arrow) | Dynamic wheels, complex filtering. |
| **Media Player** | GStreamer / VLC Overlay | Libmpv (Texture Mapping) | Seamless video, GPU acceleration. |
| **Rendering** | SDL Surfaces / OGL | WGPU (DX12/Vulkan) | Runs better on low-end/modern OS. |
| **List Logic** | Instantiated Objects | Virtualized (Windowing) | Massive RAM savings, smooth scroll. |
| **Concurrency** | Single/Rough Threading | Rust Async (Tokio) | Non-blocking UI, crash safety. |

This report serves as the strategic blueprint for your development, aligning technical choices with the specific goals of speed, scalability, and modern feature sets.

#### **Works cited**

1. LaunchBox Platform XML \- eXo Wiki, accessed January 3, 2026, [https://wiki.retro-exo.com/index.php/LaunchBox\_Platform\_XML](https://wiki.retro-exo.com/index.php/LaunchBox_Platform_XML)  
2. LaunchBox for Windows Latest Changes, accessed January 3, 2026, [https://www.launchbox-app.com/about/changelog](https://www.launchbox-app.com/about/changelog)  
3. Top 5 Rust Frameworks (2025) \- DEV Community, accessed January 3, 2026, [https://dev.to/masteringbackend/top-5-rust-frameworks-2025-3jnc](https://dev.to/masteringbackend/top-5-rust-frameworks-2025-3jnc)  
4. Thoughts on using Rust for game engine development? : r/gameenginedevs \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/gameenginedevs/comments/1lnam0o/thoughts\_on\_using\_rust\_for\_game\_engine\_development/](https://www.reddit.com/r/gameenginedevs/comments/1lnam0o/thoughts_on_using_rust_for_game_engine_development/)  
5. Official Rust implementation of Apache Arrow \- GitHub, accessed January 3, 2026, [https://github.com/apache/arrow-rs](https://github.com/apache/arrow-rs)  
6. Rust \- Apache Arrow, accessed January 3, 2026, [https://arrow.apache.org/rust/arrow/index.html](https://arrow.apache.org/rust/arrow/index.html)  
7. Rust Cpp Interop via Cxx, Autocxx / any best practices out there \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/rust/comments/14dfs78/rust\_cpp\_interop\_via\_cxx\_autocxx\_any\_best/](https://www.reddit.com/r/rust/comments/14dfs78/rust_cpp_interop_via_cxx_autocxx_any_best/)  
8. Tools to mix Rust and C++: bindgen, CXX, autobindgen, CXX-Qt and more | KDAB, accessed January 3, 2026, [https://www.kdab.com/mixing-c-and-rust-for-fun-and-profit-part-3/](https://www.kdab.com/mixing-c-and-rust-for-fun-and-profit-part-3/)  
9. Why I chose Tauri \- Practical advice on picking the right Rust GUI solution for you \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/rust/comments/1ihv7y9/why\_i\_chose\_tauri\_practical\_advice\_on\_picking\_the/](https://www.reddit.com/r/rust/comments/1ihv7y9/why_i_chose_tauri_practical_advice_on_picking_the/)  
10. Best GUI/UI libraries/packages? \- The Rust Programming Language Forum, accessed January 3, 2026, [https://users.rust-lang.org/t/best-gui-ui-libraries-packages/133830](https://users.rust-lang.org/t/best-gui-ui-libraries-packages/133830)  
11. How do popular Rust UI libraries compare? Iced vs Slint vs Egui \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/rust/comments/1iavpit/how\_do\_popular\_rust\_ui\_libraries\_compare\_iced\_vs/](https://www.reddit.com/r/rust/comments/1iavpit/how_do_popular_rust_ui_libraries_compare_iced_vs/)  
12. Introducing Minarrow — Apache Arrow implementation for HPC, Native Streaming, and Embedded Systems : r/rust \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/rust/comments/1nad0us/introducing\_minarrow\_apache\_arrow\_implementation/](https://www.reddit.com/r/rust/comments/1nad0us/introducing_minarrow_apache_arrow_implementation/)  
13. Why REST and JDBC Are Killing Your Data Stack — Flight SQL to the Rescue \- MotherDuck, accessed January 3, 2026, [https://motherduck.com/blog/flight-sql-vs-rest-vs-jdbc/](https://motherduck.com/blog/flight-sql-vs-rest-vs-jdbc/)  
14. Tip of the Week: Data Engineering with SQL, Arrow and DuckDB, accessed January 3, 2026, [https://cu-dbmi.github.io/set-website/2022/12/05/Data-Engineering-with-SQL-Arrow-and-DuckDB.html](https://cu-dbmi.github.io/set-website/2022/12/05/Data-Engineering-with-SQL-Arrow-and-DuckDB.html)  
15. DuckDB Meets Apache Arrow \- GoodData, accessed January 3, 2026, [https://www.gooddata.com/blog/duckdb-meets-apache-arrow/](https://www.gooddata.com/blog/duckdb-meets-apache-arrow/)  
16. VGMS (Video Game Metadata Schema) :: Show Detail \- The Registry\!, accessed January 3, 2026, [http://metadataregistry.org/uri/schema/VGMS](http://metadataregistry.org/uri/schema/VGMS)  
17. Video Game Metadata Schema \- Boise State University, accessed January 3, 2026, [https://experts.boisestate.edu/en/publications/video-game-metadata-schema/](https://experts.boisestate.edu/en/publications/video-game-metadata-schema/)  
18. Introduction \- Apache Arrow \[Rust\] \- GitHub Pages, accessed January 3, 2026, [https://elferherrera.github.io/arrow\_guide/introduction.html](https://elferherrera.github.io/arrow_guide/introduction.html)  
19. Metadata Providers \- RomM, accessed January 3, 2026, [https://docs.romm.app/latest/Getting-Started/Metadata-Providers/](https://docs.romm.app/latest/Getting-Started/Metadata-Providers/)  
20. Implementing faceted search with dynamic faceting (code included) \- Algolia, accessed January 3, 2026, [https://www.algolia.com/blog/engineering/implementing-faceted-search-with-dynamic-faceting-with-code](https://www.algolia.com/blog/engineering/implementing-faceted-search-with-dynamic-faceting-with-code)  
21. Smart Playlist Plugin \- beets, accessed January 3, 2026, [https://beets.readthedocs.io/en/stable/plugins/smartplaylist.html](https://beets.readthedocs.io/en/stable/plugins/smartplaylist.html)  
22. Optimizing React Performance with Virtualization: A Developer's Guide \- DEV Community, accessed January 3, 2026, [https://dev.to/usman\_awan\_003/optimizing-react-performance-with-virtualization-a-developers-guide-3j14](https://dev.to/usman_awan_003/optimizing-react-performance-with-virtualization-a-developers-guide-3j14)  
23. List Virtualization \- Patterns.dev, accessed January 3, 2026, [https://www.patterns.dev/vanilla/virtual-lists/](https://www.patterns.dev/vanilla/virtual-lists/)  
24. Need Help with Table Virtualization for Large Data Sets (100k+ rows, 50+ columns) \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/reactjs/comments/1fb9poc/need\_help\_with\_table\_virtualization\_for\_large/](https://www.reddit.com/r/reactjs/comments/1fb9poc/need_help_with_table_virtualization_for_large/)  
25. What's the best way to handle "texture streaming pool over" in unreal engine 4? Should I lower quality or quantity of textures? \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/unrealengine/comments/1kpi6nq/whats\_the\_best\_way\_to\_handle\_texture\_streaming/](https://www.reddit.com/r/unrealengine/comments/1kpi6nq/whats_the_best_way_to_handle_texture_streaming/)  
26. Texture Streaming \- Unity \- Manual, accessed January 3, 2026, [https://docs.unity3d.com/2019.1/Documentation/Manual/TextureStreaming.html](https://docs.unity3d.com/2019.1/Documentation/Manual/TextureStreaming.html)  
27. Generating Texture Atlases for Optimized Assets | by Bandinopla \- Medium, accessed January 3, 2026, [https://medium.com/@pablobandinopla/generating-texture-atlases-for-optimized-assets-63fd7a04021f](https://medium.com/@pablobandinopla/generating-texture-atlases-for-optimized-assets-63fd7a04021f)  
28. FastAtlas: Real-Time Compact Atlases for Texture Space Shading \- arXiv, accessed January 3, 2026, [https://arxiv.org/html/2502.17712v1](https://arxiv.org/html/2502.17712v1)  
29. How is mpv better than vlc? \- Hacker News, accessed January 3, 2026, [https://news.ycombinator.com/item?id=32442505](https://news.ycombinator.com/item?id=32442505)  
30. Use of libmpv as core instead of VLC \- SKYBOX, accessed January 3, 2026, [https://forum.skybox.xyz/d/765-use-of-libmpv-as-core-instead-of-vlc](https://forum.skybox.xyz/d/765-use-of-libmpv-as-core-instead-of-vlc)  
31. My custom RetroFE (CoinOPS frontend) build : r/LegendsUltimate \- Reddit, accessed January 3, 2026, [https://www.reddit.com/r/LegendsUltimate/comments/ffhqq7/my\_custom\_retrofe\_coinops\_frontend\_build/](https://www.reddit.com/r/LegendsUltimate/comments/ffhqq7/my_custom_retrofe_coinops_frontend_build/)