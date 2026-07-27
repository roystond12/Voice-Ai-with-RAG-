import { APP_NAME } from "../config";

export default function TopBar() {
  return (
    <div className="topbar">
      <div className="topbar__brand">
        <span className="topbar__logo">V</span>
        {APP_NAME}
      </div>
      <div className="topbar__avatar" aria-hidden="true" />
    </div>
  );
}
