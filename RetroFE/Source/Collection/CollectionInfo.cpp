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
#include "CollectionInfo.h"
#include "Item.h"
#include "../Database/Configuration.h"
#include "../Utility/Utils.h"
#include "../Utility/Log.h"
#include <sstream>
#include <fstream>
#include <algorithm>
#include <exception>
#include <sys/stat.h>
#include <sys/types.h>

#ifdef _WIN32
#include <Windows.h>
#endif

#if defined(__linux) || defined(__APPLE__)
#include <errno.h>
#include <cstring>
#endif

CollectionInfo::CollectionInfo(std::string name,
                               std::string listPath,
                               std::string extensions,
                               std::string metadataType,
                               std::string metadataPath)
    : name(name)
    , listpath(listPath)
    , saveRequest(false)
    , metadataType(metadataType)
    , menusort(true)
    , subsSplit(false)
    , hasSubs(false)
    , metadataPath_(metadataPath)
	, extensions_(extensions)
    , currentSort(SortType::TITLE)
    , playerFilterState(0)
{
}

CollectionInfo::~CollectionInfo()
{
    Playlists_T::iterator pit = playlists.begin();

    while(pit != playlists.end())
    {
        if(pit->second != &items)
        {
            delete pit->second;
        }
        playlists.erase(pit);
        pit = playlists.begin();
    }

	std::vector<Item *>::iterator it = items.begin();
    while(it != items.end())
    {
        delete *it;
        items.erase(it);
        it = items.begin();
    }
}

bool CollectionInfo::Save() 
{
    bool retval = true;
    if(saveRequest)
    {
        std::string dir  = Utils::combinePath(Configuration::absolutePath, "collections", name, "playlists");
        std::string file = Utils::combinePath(Configuration::absolutePath, "collections", name, "playlists/favorites.txt");
        Logger::write(Logger::ZONE_INFO, "Collection", "Saving " + file);

        std::ofstream filestream;
        try
        {
            // Create playlists directory if it does not exist yet.
            struct stat info;
            if ( stat( dir.c_str(), &info ) != 0 )
            {
#if defined(_WIN32) && !defined(__GNUC__)
                if(!CreateDirectory(dir.c_str(), NULL))
                {
                    if(ERROR_ALREADY_EXISTS != GetLastError())
                    {
                        Logger::write(Logger::ZONE_WARNING, "Collection", "Could not create directory " + dir);
                        return false;
                    }
                }
#else 
#if defined(__MINGW32__)
                if(mkdir(dir.c_str()) == -1)
#else
                if(mkdir(dir.c_str(), 0755) == -1)
#endif        
                {
                    Logger::write(Logger::ZONE_WARNING, "Collection", "Could not create directory " + dir);
                    return false;
                }
#endif
            }
            else if ( !(info.st_mode & S_IFDIR) )
            {
                Logger::write(Logger::ZONE_WARNING, "Collection", dir + " exists, but is not a directory.");
                return false;
            }

            filestream.open(file.c_str());
            std::vector<Item *> *saveitems = playlists["favorites"];
            for(std::vector<Item *>::iterator it = saveitems->begin(); it != saveitems->end(); it++)
            {
                if ((*it)->collectionInfo->name == name)
                {
                    filestream << (*it)->name << std::endl;
                }
                else
                {
                    filestream << "_" << (*it)->collectionInfo->name << ":" << (*it)->name << std::endl;
                }
            }

            filestream.close();
        }
        catch(std::exception &)
        {
            Logger::write(Logger::ZONE_ERROR, "Collection", "Save failed: " + file);
            retval = false;
        }
    }
    
    return retval;
}


std::string CollectionInfo::settingsPath() const
{
    return Utils::combinePath(Configuration::absolutePath, "collections", name);
}


void CollectionInfo::extensionList(std::vector<std::string> &extensionlist)
{
    std::istringstream ss(extensions_);
    std::string token;

    while(std::getline(ss, token, ','))
    {
        token = Utils::trimEnds(token);
    	extensionlist.push_back(token);
    }
}

std::string CollectionInfo::lowercaseName()
{
    std::string lcstr = name;
    std::transform(lcstr.begin(), lcstr.end(), lcstr.begin(), ::tolower);
    return lcstr;
}

void CollectionInfo::addSubcollection(CollectionInfo *newinfo)
{
    items.insert(items.begin(), newinfo->items.begin(), newinfo->items.end());
}

void CollectionInfo::cycleSort()
{
    int next = (int)currentSort + 1;
    if (next > (int)SortType::SCORE) {
        next = 0;
    }
    currentSort = (SortType)next;
    sortItems();
}

bool CollectionInfo::compareItems(Item *lhs, Item *rhs)
{
    // Always respect folders first logic
    if(lhs->leaf && !rhs->leaf) return true;
    if(!lhs->leaf && rhs->leaf) return false;
    
    // Subcollection split logic
    if(lhs->collectionInfo->subsSplit && lhs->collectionInfo != rhs->collectionInfo)
        return lhs->collectionInfo->lowercaseName() < rhs->collectionInfo->lowercaseName();

    // Menu sort check (if disabled, preserve order - mostly relevant for initialization)
    if(!lhs->collectionInfo->menusort && !lhs->leaf && !rhs->leaf)
        return false;

    // Actual sorting logic
    switch(currentSort) {
        case SortType::YEAR:
             if (lhs->year != rhs->year) return lhs->year < rhs->year;
             break;
        case SortType::PLAYERS:
             if (lhs->numberPlayers != rhs->numberPlayers) return lhs->numberPlayers < rhs->numberPlayers;
             break;
        case SortType::MANUFACTURER:
             if (lhs->manufacturer != rhs->manufacturer) return lhs->manufacturer < rhs->manufacturer;
             break;
        case SortType::GENRE:
             if (lhs->genre != rhs->genre) return lhs->genre < rhs->genre;
             break;
        case SortType::RATING:
             if (lhs->rating != rhs->rating) return lhs->rating > rhs->rating; // Higher rating first?
             break;
        case SortType::SCORE:
             if (lhs->score != rhs->score) return lhs->score > rhs->score; // Higher score first?
             break;
        case SortType::TITLE:
        default:
             break;
    }

    // Fallback to title
    return lhs->lowercaseFullTitle() < rhs->lowercaseFullTitle();
}

bool CollectionInfo::itemIsLess(Item *lhs, Item *rhs)
{
    if(lhs->leaf && !rhs->leaf) return true;
    if(!lhs->leaf && rhs->leaf) return false;
    if(lhs->collectionInfo->subsSplit && lhs->collectionInfo != rhs->collectionInfo)
        return lhs->collectionInfo->lowercaseName() < rhs->collectionInfo->lowercaseName();
    if(!lhs->collectionInfo->menusort && !lhs->leaf && !rhs->leaf)
        return false;
    return lhs->lowercaseFullTitle() < rhs->lowercaseFullTitle();
}


void CollectionInfo::sortItems()
{
    // Use lambda to call member function
    std::sort( items.begin(), items.end(), [this](Item* a, Item* b) {
        return this->compareItems(a, b);
    });
}

void CollectionInfo::togglePlayerFilter()
{
    // Cycle state: 0(All) -> 1(1P) -> 2(2P) -> 3(4P) -> 0
    playerFilterState++;
    if (playerFilterState > 3) playerFilterState = 0;

    Logger::write(Logger::ZONE_INFO, "CollectionInfo", "Toggling Player Filter. New State: " + Utils::toString(playerFilterState));

    // Restore original items if we have them
    if (!originalItems.empty()) {
        items = originalItems;
    } else {
        // First time filtering, save original items
        originalItems = items;
    }

    // If state is 0, we just restored, so we are done (but need to re-sort)
    if (playerFilterState == 0) {
        originalItems.clear(); // Clear backup to save memory/reset
        sortItems();
        return;
    }

    std::vector<Item *> filteredItems;
    std::string targetPlayers;
    
    if (playerFilterState == 1) targetPlayers = "1";
    else if (playerFilterState == 2) targetPlayers = "2";
    else if (playerFilterState == 3) targetPlayers = "4";

    // Filter
    for (std::vector<Item *>::iterator it = items.begin(); it != items.end(); ++it) {
        // Simple string check. Note: Metadata might be "1-2" or similar.
        // For now, strict match or "contains" logic might be needed.
        // Let's assume the metadata is clean "1", "2", "4" based on user request.
        // Or check if it CONTAINS the digit.
        if ((*it)->numberPlayers.find(targetPlayers) != std::string::npos) {
            filteredItems.push_back(*it);
        }
    }

    items = filteredItems;
    sortItems();
}

void CollectionInfo::sortPlaylists()
{
    std::vector<Item *> *allItems = &items;
    std::vector<Item *> toSortItems;

    for ( Playlists_T::iterator itP = playlists.begin( ); itP != playlists.end( ); itP++ )
    {
        if ( itP->second != allItems )
        {
            toSortItems.clear();
            for(std::vector <Item *>::iterator itSort = itP->second->begin(); itSort != itP->second->end(); itSort++)
            {
                toSortItems.push_back((*itSort));
            }
            itP->second->clear();
            for(std::vector <Item *>::iterator itAll = allItems->begin(); itAll != allItems->end(); itAll++)
            {
                for(std::vector <Item *>::iterator itSort = toSortItems.begin(); itSort != toSortItems.end(); itSort++)
                {
                    if ((*itAll) == (*itSort))
                    {
                        itP->second->push_back((*itAll));
                    }
                }
            }
        }
    }
}
