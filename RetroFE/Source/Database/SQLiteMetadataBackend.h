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

#include "IMetadataBackend.h"
#include <string>

class DB;
class Configuration;

/**
 * SQLite-based metadata storage backend.
 *
 * This is the original RetroFE metadata implementation, storing game
 * metadata in a SQLite database (meta.db). It supports importing from
 * HyperList XML, MAME XML, and EmuArc DAT formats.
 *
 * Schema:
 *   Meta(collectionName, name, title, year, manufacturer, developer,
 *        genre, cloneOf, players, ctrltype, buttons, joyways, rating, score)
 */
class SQLiteMetadataBackend : public IMetadataBackend
{
public:
    SQLiteMetadataBackend(DB& db, Configuration& config);
    ~SQLiteMetadataBackend() override;

    // IMetadataBackend interface
    bool initialize() override;
    bool resetDatabase() override;
    bool needsRefresh() override;
    void injectMetadata(CollectionInfo* collection) override;
    void injectItemMetadata(Item* item) override;
    bool importHyperlist(const std::string& hyperlistFile,
                         const std::string& collectionName) override;
    bool importMamelist(const std::string& filename,
                        const std::string& collectionName) override;
    bool importEmuArclist(const std::string& filename) override;
    bool importDirectory() override;
    std::string backendName() const override { return "SQLite"; }

private:
    /**
     * Recursively get the newest modification time in a directory tree.
     * Used to check if metadata sources have changed.
     */
    time_t timeDir(const std::string& path);

    DB& db_;
    Configuration& config_;
};
