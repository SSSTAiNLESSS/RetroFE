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


#include <vector>
#include "Component.h"
#include "../Animate/Tween.h"
#include "../Page.h"
#include "../ViewInfo.h"
#include "../../Database/Configuration.h"
#include <SDL2/SDL.h>


class Configuration;
class Font;

class ScrollingList : public Component
{

public:

    ScrollingList( Configuration &c,
                   Page          &p,
                   bool          layoutMode,
                   bool          commonMode,
                   Font         *font,
                   std::string   layoutKey,
                   std::string   imageType,
                   std::string   videoType,
                   bool          playlistMode = false );

    ScrollingList( const ScrollingList &copy );
// ... (omitted middle for brevity in planning)
    bool horizontalScroll;
    bool isPlaylistMode() { return playlistMode_; }
// ...
private:
// ...
    bool layoutMode_;
    bool commonMode_;
    bool playlistMode_;
    std::vector<Component *> *spriteList_;
    std::vector<ViewInfo *> *scrollPoints_;
    std::vector<AnimationEvents *> *tweenPoints_;

    unsigned int itemIndex_;
    unsigned int selectedOffsetIndex_;

    float scrollAcceleration_;
    float startScrollTime_;
    float minScrollTime_;
    float scrollPeriod_;

    Configuration &config_;
    Font          *fontInst_;
    std::string    layoutKey_;
    std::string    imageType_;
    std::string    videoType_;

    std::vector<Item *>     *items_;
    std::vector<Component *> components_;

};
