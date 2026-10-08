# ---------------------------------------------------------------------------
# PROJECT: NIGHTFALL - GBA endless zombie survival
#
#   make            release build  -> nightfall.gba
#   make DEBUG=1    debug build    -> nightfall_debug.gba (debug overlay + cheats)
#   make BOT=1      self-playing stress-test build -> nightfall_bot.gba (BOTSMART=1: mortal kiting bot)
#   make assets     regenerate pixel art / map / audio tables (needs python3 + Pillow)
#   make run        launch the ROM in mGBA
#   make clean
#
# Works with a plain arm-none-eabi toolchain (no libgba / devkitPro needed).
# If devkitARM is installed, point PREFIX at its compiler:
#   make PREFIX=$(DEVKITARM)/bin/arm-none-eabi-
# ---------------------------------------------------------------------------
PREFIX  ?= arm-none-eabi-
CC       = $(PREFIX)gcc
OBJCOPY  = $(PREFIX)objcopy
SIZE     = $(PREFIX)size
PYTHON  ?= python3
EMU     ?= mgba

ifeq ($(BOT),1)
TARGET  := nightfall_bot
DEFS    := -DDEBUG=1 -DBOT=1 $(if $(BOTWAVE),-DBOT_WAVE=$(BOTWAVE)) $(if $(BOTENEMY),-DBOT_ENEMY=$(BOTENEMY)) $(if $(BOTQUIET),-DBOT_QUIET=1) $(if $(BOTSMART),-DBOT_SMART=1)
OPT     := -O2
else ifeq ($(DEBUG),1)
TARGET  := nightfall_debug
DEFS    := -DDEBUG=1
OPT     := -O2 -g
else
TARGET  := nightfall
DEFS    :=
OPT     := -O2
endif

BUILD    := build/$(TARGET)
SRC_DIRS := src data
INCLUDES := -Iinclude -Idata

ARCH     := -mcpu=arm7tdmi -mtune=arm7tdmi -mthumb -mthumb-interwork
CFLAGS   := $(ARCH) $(OPT) $(DEFS) $(INCLUDES) -std=gnu11 \
            -Wall -Wextra -Wno-unused-parameter \
            -ffreestanding -fno-strict-aliasing -fomit-frame-pointer \
            -fno-tree-loop-distribute-patterns -ffunction-sections -fdata-sections \
            -MMD -MP
ASFLAGS  := $(ARCH) -I include
LDFLAGS  := $(ARCH) -nostartfiles -nostdlib -Wl,-T,gba.ld -Wl,--gc-sections \
            -Wl,-Map,$(BUILD)/$(TARGET).map -Wl,--no-warn-rwx-segments

CSRC     := $(foreach d,$(SRC_DIRS),$(wildcard $(d)/*.c))
SSRC     := $(foreach d,$(SRC_DIRS),$(wildcard $(d)/*.s))
OBJS     := $(patsubst %.c,$(BUILD)/%.o,$(CSRC)) $(patsubst %.s,$(BUILD)/%.o,$(SSRC))
DEPS     := $(OBJS:.o=.d)

.PHONY: all clean run assets rom-info
all: $(TARGET).gba

$(TARGET).gba: $(BUILD)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $@
	@if command -v gbafix >/dev/null 2>&1; then gbafix $@; else $(PYTHON) tools/gbafix.py $@; fi
	@$(SIZE) $<
	@ls -l $@

$(BUILD)/$(TARGET).elf: $(OBJS) gba.ld
	$(CC) $(LDFLAGS) $(OBJS) -lgcc -o $@

$(BUILD)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/%.o: %.s
	@mkdir -p $(dir $@)
	$(CC) $(ASFLAGS) -x assembler-with-cpp -c $< -o $@

# Optional extra optimisation flags per file (hot loops): none needed yet.

assets:
	$(PYTHON) tools/gen_assets.py
	$(PYTHON) tools/gen_map.py
	$(PYTHON) tools/gen_audio.py
	$(PYTHON) tools/audio_preview.py

run: $(TARGET).gba
	$(EMU) $(TARGET).gba

clean:
	rm -rf $(BUILD) nightfall.gba nightfall_debug.gba nightfall_bot.gba

-include $(DEPS)
