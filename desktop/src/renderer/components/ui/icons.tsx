import { FontAwesomeIcon, type FontAwesomeIconProps } from "@fortawesome/react-fontawesome";
import {
  faMagnifyingGlass,
  faPenToSquare,
  faSun,
  faMoon,
  faDesktop,
  faGear,
  faInbox,
  faPaperPlane,
  faStar,
  faBoxArchive,
  faTrash,
  faTag,
  faChevronDown,
  faSparkles,
  faReply,
  faReplyAll,
  faShare,
  faEllipsis,
  faPaperclip,
  faDownload,
  faExpand,
  faCompress,
  faFilePen,
  faBold,
  faItalic,
  faUnderline,
  faPalette,
  faAlignLeft,
  faAlignCenter,
  faAlignRight,
  faAlignJustify,
  faListUl,
  faListOl,
  faIndent,
  faOutdent,
  faArrowRotateLeft,
  faArrowRotateRight,
  faLink,
  faHighlighter,
} from "@fortawesome/pro-light-svg-icons";
import { faStar as faStarSolid } from "@fortawesome/pro-solid-svg-icons";

type IconProps = Omit<FontAwesomeIconProps, "icon">;

export const IconSearch = (props: IconProps) => <FontAwesomeIcon icon={faMagnifyingGlass} {...props} />;

export const IconCompose = (props: IconProps) => <FontAwesomeIcon icon={faPenToSquare} {...props} />;

export const IconSun = (props: IconProps) => <FontAwesomeIcon icon={faSun} {...props} />;

export const IconMoon = (props: IconProps) => <FontAwesomeIcon icon={faMoon} {...props} />;

export const IconThemeSystem = (props: IconProps) => <FontAwesomeIcon icon={faDesktop} {...props} />;

export const IconGear = (props: IconProps) => <FontAwesomeIcon icon={faGear} {...props} />;

export const IconInbox = (props: IconProps) => <FontAwesomeIcon icon={faInbox} {...props} />;

export const IconSent = (props: IconProps) => <FontAwesomeIcon icon={faPaperPlane} {...props} />;

export const IconStar = ({ filled, ...props }: IconProps & { filled?: boolean }) => (
  <FontAwesomeIcon icon={filled ? faStarSolid : faStar} {...props} />
);

export const IconArchive = (props: IconProps) => <FontAwesomeIcon icon={faBoxArchive} {...props} />;

export const IconTrash = (props: IconProps) => <FontAwesomeIcon icon={faTrash} {...props} />;

export const IconTag = (props: IconProps) => <FontAwesomeIcon icon={faTag} {...props} />;

export const IconChevronDown = (props: IconProps) => <FontAwesomeIcon icon={faChevronDown} {...props} />;

export const IconSparkles = (props: IconProps) => <FontAwesomeIcon icon={faSparkles} {...props} />;

export const IconReply = (props: IconProps) => <FontAwesomeIcon icon={faReply} {...props} />;

export const IconReplyAll = (props: IconProps) => <FontAwesomeIcon icon={faReplyAll} {...props} />;

export const IconForward = (props: IconProps) => <FontAwesomeIcon icon={faShare} {...props} />;

export const IconMoreHorizontal = (props: IconProps) => <FontAwesomeIcon icon={faEllipsis} {...props} />;

export const IconSend = (props: IconProps) => <FontAwesomeIcon icon={faPaperPlane} {...props} />;

export const IconAttachment = (props: IconProps) => <FontAwesomeIcon icon={faPaperclip} {...props} />;

export const IconDownload = (props: IconProps) => <FontAwesomeIcon icon={faDownload} {...props} />;

export const IconExpand = (props: IconProps) => <FontAwesomeIcon icon={faExpand} {...props} />;

export const IconCompress = (props: IconProps) => <FontAwesomeIcon icon={faCompress} {...props} />;

export const IconDraft = (props: IconProps) => <FontAwesomeIcon icon={faFilePen} {...props} />;

export const IconBold = (props: IconProps) => <FontAwesomeIcon icon={faBold} {...props} />;

export const IconItalic = (props: IconProps) => <FontAwesomeIcon icon={faItalic} {...props} />;

export const IconUnderline = (props: IconProps) => <FontAwesomeIcon icon={faUnderline} {...props} />;

export const IconPalette = (props: IconProps) => <FontAwesomeIcon icon={faPalette} {...props} />;

export const IconHighlighter = (props: IconProps) => <FontAwesomeIcon icon={faHighlighter} {...props} />;

export const IconAlignLeft = (props: IconProps) => <FontAwesomeIcon icon={faAlignLeft} {...props} />;

export const IconAlignCenter = (props: IconProps) => <FontAwesomeIcon icon={faAlignCenter} {...props} />;

export const IconAlignRight = (props: IconProps) => <FontAwesomeIcon icon={faAlignRight} {...props} />;

export const IconAlignJustify = (props: IconProps) => <FontAwesomeIcon icon={faAlignJustify} {...props} />;

export const IconListUl = (props: IconProps) => <FontAwesomeIcon icon={faListUl} {...props} />;

export const IconListOl = (props: IconProps) => <FontAwesomeIcon icon={faListOl} {...props} />;

export const IconIndent = (props: IconProps) => <FontAwesomeIcon icon={faIndent} {...props} />;

export const IconOutdent = (props: IconProps) => <FontAwesomeIcon icon={faOutdent} {...props} />;

export const IconUndo = (props: IconProps) => <FontAwesomeIcon icon={faArrowRotateLeft} {...props} />;

export const IconRedo = (props: IconProps) => <FontAwesomeIcon icon={faArrowRotateRight} {...props} />;

export const IconLink = (props: IconProps) => <FontAwesomeIcon icon={faLink} {...props} />;

