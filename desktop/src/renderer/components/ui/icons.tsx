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
