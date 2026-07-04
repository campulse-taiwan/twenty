import { i18n } from '@lingui/core';
import { APP_LOCALES } from 'twenty-shared/translations';
import { type CommandMenuContextApi, type Nullable } from 'twenty-shared/types';
import {
  interpolateCommandMenuItemTemplate,
  isDefined,
} from 'twenty-shared/utils';
import { COMMAND_MENU_ITEM_LABEL_TRANSLATIONS_ZH_TW } from '@/command-menu-item/utils/command-menu-item-label-translations.zh-TW';
import { type CommandMenuItemFieldsFragment } from '~/generated-metadata/graphql';

const translateCommandMenuItemTemplate = (
  label: Nullable<string>,
): Nullable<string> => {
  if (!isDefined(label)) {
    return null;
  }

  if (i18n.locale === APP_LOCALES['zh-TW']) {
    return COMMAND_MENU_ITEM_LABEL_TRANSLATIONS_ZH_TW[label] ?? label;
  }

  return label;
};

type InterpolatedCommandMenuItemFields = {
  iconKey: Nullable<string>;
  label: string;
  shortLabel: Nullable<string>;
};

export const interpolateCommandMenuItemFields = (
  item: CommandMenuItemFieldsFragment,
  commandMenuContextApi: CommandMenuContextApi,
): InterpolatedCommandMenuItemFields => {
  const iconKey = interpolateCommandMenuItemTemplate({
    label: item.icon,
    context: commandMenuContextApi,
  });

  const translatedLabel = translateCommandMenuItemTemplate(item.label);

  const label =
    interpolateCommandMenuItemTemplate({
      label: translatedLabel,
      context: commandMenuContextApi,
    }) ?? translatedLabel;

  const shortLabel = interpolateCommandMenuItemTemplate({
    label: translateCommandMenuItemTemplate(item.shortLabel),
    context: commandMenuContextApi,
  });

  return { iconKey, label, shortLabel };
};
