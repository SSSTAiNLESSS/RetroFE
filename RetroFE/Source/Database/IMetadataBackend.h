/* This file is part of RetroFE.
 *
 * RetroFE is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * RetroFE is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with RetroFE.  If not, see <http://www.gnu.org/licenses/>.
 */
#pragma once

#include <string>

class CollectionInfo;
class Item;

/**
 * Abstract interface for metadata storage backends.
 *
 * This interface allows RetroFE to support multiple metadata storage
 * implementations (SQLite, Apache Arrow/Parquet, etc.) while maintaining
 * a consistent API for the rest of the application.
 *
 * Implementations:
 * - SQLiteMetadataBackend: Original SQLite-based storage (meta.db)
 * - ArrowMetadataBackend: Apache Arrow/Parquet columnar storage (future)
 */
class IMetadataBackend
{
public:
    virtual ~IMetadataBackend() = default;

    /**
     * Initialize the backend storage.
     * Creates necessary tables/files and imports metadata if needed.
     * @return true on success, false on failure
     */
    virtual bool initialize() = 0;

    /**
     * Reset/clear the backend storage.
     * Drops all metadata and recreates empty storage.
     * @return true on success, false on failure
     */
    virtual bool resetDatabase() = 0;

    /**
     * Check if metadata needs to be refreshed from source files.
     * Compares modification times of XML sources vs stored metadata.
     * @return true if refresh is needed
     */
    virtual bool needsRefresh() = 0;

    /**
     * Inject metadata into all items in a collection.
     * Populates Item fields (title, year, manufacturer, etc.) from stored metadata.
     * @param collection The collection whose items need metadata injection
     */
    virtual void injectMetadata(CollectionInfo* collection) = 0;

    /**
     * Inject metadata into a single item.
     * Used for on-demand metadata loading.
     * @param item The item to populate with metadata
     */
    virtual void injectItemMetadata(Item* item) = 0;

    /**
     * Import metadata from HyperList XML format.
     * @param hyperlistFile Path to the HyperList XML file
     * @param collectionName Name of the collection this metadata belongs to
     * @return true on success, false on failure
     */
    virtual bool importHyperlist(const std::string& hyperlistFile,
                                  const std::string& collectionName) = 0;

    /**
     * Import metadata from MAME XML format.
     * @param filename Path to the MAME XML file
     * @param collectionName Name of the collection this metadata belongs to
     * @return true on success, false on failure
     */
    virtual bool importMamelist(const std::string& filename,
                                 const std::string& collectionName) = 0;

    /**
     * Import metadata from EmuArc DAT format.
     * Collection name is extracted from the file's internal header.
     * @param filename Path to the EmuArc DAT file
     * @return true on success, false on failure
     */
    virtual bool importEmuArclist(const std::string& filename) = 0;

    /**
     * Import all metadata from the standard directories.
     * Scans hyperlist/, mamelist/, emuarc/ directories for source files.
     * @return true on success, false on failure
     */
    virtual bool importDirectory() = 0;

    /**
     * Get the name of this backend for logging/debugging.
     * @return Backend name (e.g., "SQLite", "Arrow/Parquet")
     */
    virtual std::string backendName() const = 0;
};
