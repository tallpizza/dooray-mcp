# Dooray MCP Server

Dooray API를 Claude Code와 연동하기 위한 MCP (Model Context Protocol) 서버입니다.

## 기능

이 MCP 서버는 Dooray의 주요 기능을 6개의 통합 도구로 제공합니다:

1. **dooray_tasks** - 업무 관리 (목록 조회, 상세 조회, 생성, 수정, 삭제, 상태 변경, 담당자 지정)
2. **dooray_comments** - 댓글 관리 (목록 조회, 생성, 수정, 삭제, 멘션 지원)
3. **dooray_tags** - 태그 관리 (목록 조회, 생성, 업무에 태그 추가/제거)
4. **dooray_search** - 검색 기능 (업무 검색, 담당자별/상태별/태그별/기간별 검색)
5. **dooray_members** - 사용자 관리 (이메일/ID 검색, 사용자 정보 조회, 프로젝트 멤버 목록)
6. **dooray_files** - 파일 및 이미지 관리 (업무 파일 목록, 파일 메타데이터, 파일 콘텐츠 다운로드, Content ID로 직접 접근)

## 빠른 설치

### GitHub에서 자동 설치

```bash
# 1. 저장소 클론
git clone https://github.com/tallpizza/dooray-mcp.git
cd dooray-mcp

# 2. 자동 설치 스크립트 실행
./install.sh

# 3. 환경 변수 설정 (.env 파일 수정)
# DOORAY_API_TOKEN과 DOORAY_DEFAULT_PROJECT_ID를 실제 값으로 변경

# 4. Claude Code에 추가
claude mcp add-json dooray "$(cat .mcp.json | jq -c .dooray)"
```

## 상세 설치 및 설정

### 1. GitHub에서 설치

```bash
# GitHub에서 프로젝트 클론
git clone https://github.com/tallpizza/dooray-mcp.git
cd dooray-mcp

# 종속성 설치
uv sync
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 설정합니다:

```bash
# .env.example을 복사
cp .env.example .env

# .env 파일 내용
DOORAY_API_TOKEN=your-actual-dooray-api-token
DOORAY_BASE_URL=https://api.dooray.com
DOORAY_DEFAULT_PROJECT_ID=your-default-project-id

LOG_LEVEL=INFO
```

### 3. Claude Code MCP 서버 추가

#### 방법 1: JSON으로 추가 (권장)

```bash
# 환경 변수를 포함한 완전한 설정
claude mcp add-json dooray '{
  "type": "stdio",
  "command": "uv",
  "args": ["run", "python", "-m", "dooray_mcp.server"],
  "env": {
    "DOORAY_API_TOKEN": "your-actual-dooray-api-token",
    "DOORAY_BASE_URL": "https://api.dooray.com",
    "DOORAY_DEFAULT_PROJECT_ID": "your-default-project-id"
  }
}'
```

#### 방법 2: 설정 파일 사용

```bash
# .mcp.json 설정 파일 준비
cp .mcp.json.example .mcp.json
# 환경 변수를 실제 값으로 수정

# Claude Code에서 사용
claude --mcp-config .mcp.json
```

### 4. 연결 확인

```bash
# MCP 서버 목록 확인
claude mcp list

# Dooray 서버가 ✓ Connected로 표시되는지 확인
```

### 5. 도구 테스트

```bash
# 업무 목록 조회 테스트
claude --print "dooray_tasks를 사용해서 업무 목록을 조회해주세요."

# 댓글 생성 테스트
claude --print "dooray_comments를 사용해서 댓글을 생성해주세요."
```

## 사용법

### 도구별 사용 예제

### 1. dooray_tasks (업무 관리)

```typescript
// 업무 목록 조회
{
  "action": "list",
  "projectId": "project-123"  // 선택사항 (환경 변수 사용 가능)
}

// 업무 생성
{
  "action": "create",
  "projectId": "project-123",
  "title": "새 업무",
  "description": "업무 설명",
  "priority": "normal"
}
```

### 2. dooray_comments (댓글 관리)

```typescript
// 댓글 생성 (멘션 포함)
{
  "action": "create",
  "taskId": "task-456",
  "content": "댓글 내용",
  "mentions": ["user1", "user2"]  // 선택사항
}
```

### 3. dooray_tags (태그 관리)

```typescript
// 새 태그 생성
{
  "action": "create",
  "projectId": "project-123",
  "tagName": "긴급",
  "tagColor": "#FF0000"  // # 포함 가능, 자동으로 제거됨
}

// 업무에 태그 추가
{
  "action": "add_to_task",
  "taskId": "task-456",
  "tagName": "긴급"
}
```

### 4. dooray_search (검색 기능)

```typescript
// 업무 텍스트 검색
{
  "searchType": "tasks",
  "projectId": "project-123",
  "query": "버그 수정"
}

// 상태별 검색
{
  "searchType": "by_status",
  "projectId": "project-123",
  "status": "완료"
}
```

### 5. dooray_members (사용자 관리)

```typescript
// 이메일로 사용자 검색
{
  "action": "search_by_email",
  "email": "user@company.com"
}

// 프로젝트 멤버 목록
{
  "action": "list_project_members",
  "projectId": "project-123"
}
```

### 6. dooray_files (파일 및 이미지 관리)

```typescript
// 업무 파일 목록 조회
{
  "action": "list_task_files",
  "taskId": "task-456",
  "projectId": "project-123"  // 선택사항 (환경 변수 사용 가능)
}

// 업무 파일 메타데이터 조회
{
  "action": "get_task_file_metadata",
  "taskId": "task-456",
  "fileId": "file-789",
  "projectId": "project-123"
}

// 업무 파일 콘텐츠 다운로드 (base64 인코딩)
{
  "action": "get_task_file_content",
  "taskId": "task-456",
  "fileId": "file-789",
  "projectId": "project-123"
}

// Content ID로 직접 파일 메타데이터 조회 (Drive API)
{
  "action": "get_drive_file_metadata",
  "fileId": "content-id-xyz"
}

// Content ID로 직접 파일 콘텐츠 다운로드 (Drive API)
{
  "action": "get_drive_file_content",
  "fileId": "content-id-xyz"
}
```

## API 정보

- **Base URL**: `https://api.dooray.com`
- **인증**: `Authorization: dooray-api {TOKEN}`
- **업무 관리**: `/project/v1/projects/{projectId}/posts`
- **댓글 관리**: `/project/v1/projects/{projectId}/posts/{taskId}/logs`
- **태그 관리**: `/project/v1/projects/{projectId}/tags`
- **사용자 관리**: `/common/v1/members`
- **파일 관리**: `/project/v1/projects/{projectId}/posts/{taskId}/files`
- **Drive 파일**: `/drive/v1/files/{fileId}`

## 문제 해결

### 연결 문제
1. **인증 오류**: `DOORAY_API_TOKEN`이 올바른지 확인
2. **프로젝트 ID 오류**: `DOORAY_DEFAULT_PROJECT_ID`가 존재하는 프로젝트인지 확인
3. **권한 오류**: API 토큰이 해당 프로젝트에 대한 권한을 가지고 있는지 확인

### MCP 연결 문제
1. **서버 연결 실패**: `claude mcp list`에서 상태 확인
2. **도구 인식 실패**: MCP 서버 재시작 또는 Claude Code 재시작
3. **권한 문제**: `--dangerously-skip-permissions` 플래그 사용 (개발 환경에서만)

## 개발 및 기여

이 프로젝트는 MIT 라이센스 하에 배포되며, 버그 리포트와 기능 요청을 환영합니다.

## 버전 정보

- **버전**: 1.0.0
- **Python**: 3.8+
- **MCP**: 1.0.0+
- **HTTP 클라이언트**: httpx 0.25.0+